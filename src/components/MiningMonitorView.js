import React, { useEffect, useState } from 'react';
import axios from 'axios';

function MiningMonitorView() {
  const [miningStatus, setMiningStatus] = useState({
    status: "Idle",
    attempts: 0,
    current_hash: "",
  });

  const fetchMiningStatus = async () => {
    try {
      const response = await axios.get('http://localhost:5000/mining-status');
      setMiningStatus(response.data);
    } catch (error) {
      console.error('Error fetching mining status:', error);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      fetchMiningStatus();
    }, 1000); // Poll every second

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return (
    <div className="mining-monitor">
      <h2>Mining Monitor</h2>
      <p><strong>Status:</strong> {miningStatus.status}</p>
      <p><strong>Attempts:</strong> {miningStatus.attempts}</p>
      <p><strong>Current Hash Attempt:</strong> {miningStatus.current_hash}</p>
    </div>
  );
}

export default MiningMonitorView;
