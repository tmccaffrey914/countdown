import React from 'react';
import './App.css';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedLetters: [],
      timer: 35
    };
    this.countdownInterval = null;
  }

  countdown = () => {
    if (this.state.timer > 0) {
      this.setState((prevState) => {
        return {
          timer: prevState.timer - 1
        }
      })
    } else {
      clearInterval(this.countdownInterval);
      this.setState({
        timer: 35
      })
    }
  };

  getConsonant = () => {
    if ( this.state.selectedLetters.length >= 9 ) {
      if (this.state.timer === 35) {
        this.countdownInterval = setInterval(this.countdown, 1000);
      }
      return
    }

    // TODO: Pull out to API File
    fetch('/consonant', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    }).then((response) => {
      return response.json();
    }).then((data) => {
      let tempLetters = this.state.selectedLetters;
      tempLetters.push(data["consonant"].toUpperCase());
      this.setState({
        selectedLetters: tempLetters
      });
    });
  };

  getVowel = () => {
    if ( this.state.selectedLetters.length >= 9 ) {
      if (this.state.timer === 35) {
        this.countdownInterval = setInterval(this.countdown, 1000);
      }
      return
    }

    // TODO: Pull out to API File
    fetch('/vowel', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    }).then((response) => {
      return response.json();
    }).then((data) => {
      let tempLetters = this.state.selectedLetters;
      tempLetters.push(data["vowel"].toUpperCase());
      this.setState({
          selectedLetters: tempLetters
      });
    });
  };

  displayBoard = (selectedLetters) => {
    return <div className="board">
      {
        selectedLetters.map((letter) => {
          return <span className="letter-card">{letter}</span>
        })
      }
    </div>
  };

  render() {
    return <div className="App">
      <h1 className="App-header">COUNTDOWN</h1>
      <div>
        <label className="timer">{this.state.timer} Seconds Remaining</label>
      </div>
      {this.displayBoard(this.state.selectedLetters)}
      <div className="board-footer">
        <div className="buttons">
          <label className="letter-card">Vowel</label>
          <button onClick={this.getVowel}>A Vowel Please, Rachel</button>
        </div>
        <div className="buttons">
          <label className="letter-card">Consonant</label>
          <button onClick={this.getConsonant}>And another Consonant</button>
        </div>
      </div>
    </div>
  }
}

export default App;
