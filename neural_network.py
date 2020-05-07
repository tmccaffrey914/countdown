import os
import tensorflow as tf
import sys

from play import (
    decode_word,
    encode_neural_network_example,
    encode_neural_network_label,
)
from process_data import (
    DEFAULT_BATCH_SIZE,
    WORDS_DB
)

BUFFER_SIZE = 50000
BATCH_SIZE = 64
TAKE_SIZE = 5000

# Length of the vocabulary in chars
VOCAB_SIZE = 26 + 1

# The embedding dimension
EMBEDDING_DIM = 256

# Number of RNN units
RNN_UNITS = 1024

# Place to Output Saved Models as they are being trained:
CHECKPOINT_DIRECTORY = './training_checkpoints'


def step_one_load_the_data_and_label_with_expected_output():
    cursor = WORDS_DB.cursor()
    cursor.execute("USE wn_pro_mysql;")

    # This will Join the Plain Text Words Table and the Table Containing the Shuffled forms of those Words:
    cursor.execute("""
        SELECT shuffled_words.word, wn_synset.word 
        FROM wn_synset 
        INNER JOIN shuffled_words ON 
        wn_synset.synset_id = shuffled_words.synset_id AND wn_synset.w_num = shuffled_words.w_num;
    """)

    batches_of_labeled_data_sets = []

    while True:
        result = cursor.fetchmany(DEFAULT_BATCH_SIZE)

        if not result:
            break

        # The following code will seem counter-intuitive, but it is necessary. We want our resultant
        # List format dataset to consist of Tuples - each containing Two Tensor Objects. One object being
        # the "Example" and the other being the "Label". This is why they must be processed separately
        # then brought back together.
        shuffled_values, plaintext_values = zip(*result)

        shuffled_values = [encode_neural_network_example(value) for value in shuffled_values]
        plaintext_values = [encode_neural_network_label(value) for value in plaintext_values]

        shuffled_word_dataset = tf.data.Dataset.from_tensor_slices(shuffled_values)
        plaintext_word_dataset = tf.data.Dataset.from_tensor_slices(plaintext_values)

        batches_of_labeled_data_sets.append(tf.data.Dataset.zip((shuffled_word_dataset, plaintext_word_dataset)))
    cursor.close()

    # Copied Directly From TensorFlow, Joins all of our DataSet batches together using TF Built-ins:
    all_labeled_data = batches_of_labeled_data_sets[0]
    for labeled_dataset in batches_of_labeled_data_sets[1:]:
        all_labeled_data = all_labeled_data.concatenate(labeled_dataset)

    # return all_labeled_data.shuffle(BUFFER_SIZE, reshuffle_each_iteration=False)
    return all_labeled_data


def step_two_get_train_and_test_data(all_labeled_data):
    train = all_labeled_data.skip(TAKE_SIZE)
    test = all_labeled_data.take(TAKE_SIZE)

    return train.batch(BATCH_SIZE, drop_remainder=True), test.batch(BATCH_SIZE, drop_remainder=True)


def step_three_make_the_ai_model(vocabulary_size=VOCAB_SIZE, embedding_dimension=EMBEDDING_DIM,
                                 rnn_units=RNN_UNITS, batch_size=BATCH_SIZE):
    return tf.keras.Sequential([
        tf.keras.layers.Embedding(vocabulary_size, embedding_dimension, batch_input_shape=[batch_size, None]),
        tf.keras.layers.GRU(rnn_units, return_sequences=True, stateful=True, recurrent_initializer='glorot_uniform'),
        tf.keras.layers.Dense(vocabulary_size)
    ])


def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)


def make_checkpoint_callback(checkpoint_dir=CHECKPOINT_DIRECTORY):
    # Name of the checkpoint files
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
    return tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_prefix, save_weights_only=True)


def restore_saved_network(checkpoint_dir=CHECKPOINT_DIRECTORY):
    model = step_three_make_the_ai_model(batch_size=1)
    model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    model.build(tf.TensorShape([1, None]))
    return model


def guess_word(model, jumbled_word):
    # Evaluation step (generating text using the learned model)

    # Converting our start string to numbers (vectorizing)
    input_eval = encode_neural_network_example(jumbled_word)
    input_eval = tf.expand_dims(input_eval, 0)

    # Low temperatures results in more predictable text.
    # Higher temperatures results in more surprising text.
    # Experiment to find the best setting.
    temperature = 1.0

    # Here batch size == 1
    model.reset_states()
    prediction = model(input_eval)

    # remove the batch dimension
    prediction = tf.squeeze(prediction, 0)

    # using a categorical distribution to predict the character returned by the model
    prediction = prediction / temperature

    encoded_prediction = tf.random.categorical(prediction, num_samples=1).numpy()

    return decode_word([sub_list[0] for sub_list in encoded_prediction.tolist()])


if __name__ == '__main__':
    print("Start Data Processing")
    print("TensorFlow Version: {}".format(tf.__version__))

    print("Step 1")
    labeled_data_set = step_one_load_the_data_and_label_with_expected_output()

    print("Step 2")
    train_data, test_data = step_two_get_train_and_test_data(labeled_data_set)

    print("Step 3")
    model = step_three_make_the_ai_model()
    model.compile(optimizer='adam', loss=loss)

    history = model.fit(train_data, epochs=5, callbacks=[make_checkpoint_callback()])

# if __name__ == '__main__':
#     model = restore_saved_network()
#     print(guess_word(model, "keyitnyet"))
