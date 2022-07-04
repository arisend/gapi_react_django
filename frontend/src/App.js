import "@progress/kendo-theme-material/dist/all.css";
import "hammerjs";
import "./App.css";
import React, { Component } from "react";
import axios from "axios";
import Line from "./components/Line";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      orderList: [],
    };
  }

  componentDidMount() {
    this.refreshList();
  }

  refreshList = () => {
    axios
      .get("http://localhost:8000/api/pages/?removed=False")
      .then((res) => this.setState({ orderList: res.data}))
      .catch((err) => console.log(err));
    
  };




  render() {
    return (
      <div className="App">
        <div className="container">
          <h1>Orders graph</h1>

          <div className="section">
            <Line orderList={this.state.orderList}/>
          </div>
        </div>
      </div>
    );
  }



}



export default App;