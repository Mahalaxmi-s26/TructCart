import { useState } from 'react';

import axios from 'axios';

import {
  PieChart,
  Pie,
  Cell,
  Tooltip
} from 'recharts';

function App() {

  const [material, setMaterial] = useState(0);

  const [powerUsage, setPowerUsage] = useState(0);

  const [recyclable, setRecyclable] = useState(1);

  const [carbonFootprint, setCarbonFootprint] = useState(0);

  const [result, setResult] = useState("");

  const [ecoScore, setEcoScore] = useState(0);

  const [explanation, setExplanation] = useState("");

  // PIE CHART DATA

  const chartData = [

    {
      name: "Eco Score",
      value: Number(ecoScore)
    },

    {
      name: "Remaining",
      value: 100 - Number(ecoScore)
    }
  ];

  // BUTTON FUNCTION

  const analyzeProduct = async () => {

    try {

      const response = await axios.post(
        'http://localhost:3001/analyze',
        {
          material: Number(material),
          power_usage: Number(powerUsage),
          recyclable: Number(recyclable),
          carbon_footprint: Number(carbonFootprint)
        }
      );

      console.log(response.data);

      setResult(response.data.prediction);

      setEcoScore(response.data.eco_score);

      setExplanation(response.data.explanation);

    } catch (error) {

      console.log(error);

      alert("Error connecting to backend");
    }
  };

  return (

    <div style={{
      padding: "40px",
      fontFamily: "Arial"
    }}>

      <h1>AI Sustainable Electronics Product Analyzer</h1>

      <h3>Material</h3>

      <select onChange={(e) => setMaterial(e.target.value)}>

        <option value="0">Glass</option>

        <option value="1">Metal</option>

        <option value="2">Plastic</option>

      </select>

      <h3>Power Usage</h3>

      <select onChange={(e) => setPowerUsage(e.target.value)}>

        <option value="0">Low</option>

        <option value="1">Medium</option>

        <option value="2">High</option>

      </select>

      <h3>Recyclable</h3>

      <select onChange={(e) => setRecyclable(e.target.value)}>

        <option value="1">Yes</option>

        <option value="0">No</option>

      </select>

      <h3>Carbon Footprint</h3>

      <select onChange={(e) => setCarbonFootprint(e.target.value)}>

        <option value="0">Low</option>

        <option value="1">Medium</option>

        <option value="2">High</option>

      </select>

      <br />
      <br />

      <button
        onClick={analyzeProduct}
        style={{
          padding: "12px",
          fontSize: "18px",
          cursor: "pointer"
        }}
      >
        Analyze Product
      </button>

      <br />
      <br />

      <h2>{result}</h2>

      <h2>Eco Score: {ecoScore}%</h2>

      <p>{explanation}</p>

      <h2>Eco Score Analysis</h2>

      <PieChart width={400} height={300}>

        <Pie
          data={chartData}
          dataKey="value"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label
        >

          <Cell fill="#00C49F" />

          <Cell fill="#FF8042" />

        </Pie>

        <Tooltip />

      </PieChart>

    </div>
  );
}

export default App;