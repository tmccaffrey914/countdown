
## Dev Setup

Prerequisites:
```angular2
brew install node
brew install git
brew install python
brew install mysql
```

Pull down the Repo:
```angular2
git clone git@github.com:tmccaffrey914/countdown.git
cd countdown
```

Set up a virtual environment:
```angular2
virtualenv venv
source venv/bin/activate
```

Install 3rd Party Dependencies:
```
pip install tensorflow
pip install tensorflow_datasets
pip install cherrypy
pip install mysql-connector
```

Import the DB:
```angular2
brew services start mysql
mysql -u root dictionary_db < data/wordnet20-from-prolog-all-3.sql
```

Ensure Data is there:
```angular2
mysql -u root
```

Set up UI:
```angular2
npm install
npm run build (npm run start)
```

## How to use:
1. First prepare the DB data by running the `process_data.py` file.
2. Next, prepare and save a Neural Network by running `neural_network.py` file.
3. Finally, the app should be ready to run. So start the webserver by running `webserver.py` & in the CLI run: `npm start`
4. App will be available at http://localhost:3000 
