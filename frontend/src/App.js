import { useState } from 'react';
import axios from 'axios';

function App() {

  // STATES

  const [material, setMaterial] = useState(0);
  const [powerUsage, setPowerUsage] = useState(0);
  const [recyclable, setRecyclable] = useState(0);
  const [carbonFootprint, setCarbonFootprint] = useState(0);

  const [result, setResult] = useState("");
  const [ecoScore, setEcoScore] = useState("");
  const [explanation, setExplanation] = useState("");

  // ANALYZE FUNCTION

  const analyzeProduct = async () => {

    try {

      const response = await axios.post(
        'http://localhost:3001/analyze',
        {
          material: parseInt(material),
          power_usage: parseInt(powerUsage),
          recyclable: parseInt(recyclable),
          carbon_footprint: parseInt(carbonFootprint)
        }
      );

      // SET RESULTS

      setResult(response.data.prediction);

      setEcoScore(response.data.eco_score);

      setExplanation(response.data.explanation);

    } catch (error) {

      console.log(error);
    }
  };

  // UI

  return (

    <div style={{
      padding: "40px",
      fontFamily: "Arial"
    }}>

      <h1>AI Sustainable Electronics Product Analyzer</h1>

      {/* MATERIAL */}

      <h3>Material</h3>

      <select onChange={(e) => setMaterial(e.target.value)}>

        <option value="0">Glass</option>

        <option value="1">Metal</option>

        <option value="2">Plastic</option>

      </select>

      {/* POWER */}

      <h3>Power Usage</h3>

      <select onChange={(e) => setPowerUsage(e.target.value)}>

        <option value="0">Low</option>

        <option value="1">Medium</option>

        <option value="2">High</option>

      </select>

      {/* RECYCLABLE */}

      <h3>Recyclable</h3>

      <select onChange={(e) => setRecyclable(e.target.value)}>

        <option value="1">Yes</option>

        <option value="0">No</option>

      </select>

      {/* CARBON */}

      <h3>Carbon Footprint</h3>

      <select onChange={(e) => setCarbonFootprint(e.target.value)}>

        <option value="0">Low</option>

        <option value="1">Medium</option>

        <option value="2">High</option>

      </select>

      <br />
      <br />

      {/* BUTTON */}

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

      {/* RESULTS */}

      <h2>{result}</h2>

      <h2>Eco Score: {ecoScore}%</h2>

      <p>{explanation}</p>

    </div>
  );
}

export default App;