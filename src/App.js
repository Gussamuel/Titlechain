import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';
import MiningMonitorView from './components/MiningMonitorView'; // Import Mining Monitor View

function App() {
  const [view, setView] = useState('blockchain');
  const [blockchain, setBlockchain] = useState([]);
  const [pendingTransactions, setPendingTransactions] = useState([]);
  const [totalFees, setTotalFees] = useState(0);
  const [searchResults, setSearchResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    fee: 0,
    private_key:
      'acfb5657e6b35f266fb3df6ee7e2a844618d7f4afaf31cd17934f31710ff96c3d548bfe2399041d339724034e894d772',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const submitTransaction = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/transactions/new', {
        form_data: {
          first_name: formData.first_name,
          last_name: formData.last_name,
        },
        fee: parseFloat(formData.fee),
        private_key: formData.private_key,
      });

      alert('Transaction submitted successfully!');
      fetchPendingTransactions();
      fetchBlockchain(); // Refresh blockchain view to show new blocks
    } catch (error) {
      console.error('Error submitting transaction:', error);
      alert('Failed to submit transaction. Check the console for errors.');
    }
  };

  const fetchBlockchain = async () => {
    try {
      const response = await axios.get('http://localhost:5000/chain');
      setBlockchain(response.data.chain);
    } catch (error) {
      console.error('Error fetching blockchain:', error);
    }
  };

  const fetchPendingTransactions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/transactions/pending');
      setPendingTransactions(response.data);
    } catch (error) {
      console.error('Error fetching pending transactions:', error);
    }
  };

  const fetchTotalFees = async () => {
    try {
      const response = await axios.get('http://localhost:5000/fees');
      setTotalFees(response.data.total_fees_collected);
    } catch (error) {
      console.error('Error fetching total fees:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`http://localhost:5000/search?q=${searchQuery}`);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error during search:', error);
    }
  };

  useEffect(() => {
    fetchBlockchain();
    fetchPendingTransactions();
    fetchTotalFees();
  }, []);

  return (
    <div className="app-container">
      <h1>TitleChain Blockchain</h1>
      <div className="menu">
        <button onClick={() => setView('blockchain')}>View Blockchain</button>
        <button onClick={() => setView('pending')}>Pending Transactions</button>
        <button onClick={() => setView('new')}>Submit Transaction</button>
        <button onClick={() => setView('search')}>Search</button>
        <button onClick={() => setView('fees')}>Total Fees</button>
        <button onClick={() => setView('mining')}>Mining Monitor</button> {/* New Button */}
      </div>

      {view === 'blockchain' && <BlockchainView blockchain={blockchain} />}
      {view === 'pending' && <PendingTransactionsView transactions={pendingTransactions} />}
      {view === 'new' && (
        <TransactionForm
          formData={formData}
          handleChange={handleChange}
          submitTransaction={submitTransaction}
        />
      )}
      {view === 'search' && (
        <SearchView
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          handleSearch={handleSearch}
          results={searchResults}
        />
      )}
      {view === 'fees' && <TotalFeesView totalFees={totalFees} />}
      {view === 'mining' && <MiningMonitorView />} {/* Mining Monitor View */}
    </div>
  );
}

function BlockchainView({ blockchain }) {
  return (
    <div className="blockchain-container">
      <h2>Blockchain Viewer</h2>
      {blockchain.map((block, blockIndex) => (
        <div key={block.index} className="block">
          <div className="block-header">
            <h3>Block {block.index}</h3>
            <p><strong>Hash:</strong> {block.hash}</p>
            <p><strong>Previous Hash:</strong> {block.previous_hash}</p>
          </div>

          <div className="transactions">
            {block.transactions.map((tx, idx) => (
              <div key={idx} className="transaction">
                <p><strong>Transaction {idx + 1}</strong></p>
                <p>{tx.form_data.first_name} {tx.form_data.last_name} (Fee: ${tx.fee})</p>
              </div>
            ))}
          </div>

          {blockIndex < blockchain.length - 1 && (
            <div className="arrow">
              ➡️
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function PendingTransactionsView({ transactions }) {
  return (
    <div>
      <h2>Pending Transactions</h2>
      <ul>
        {transactions.map((tx, idx) => (
          <li key={idx}>
            {tx.form_data.first_name} {tx.form_data.last_name} (Fee: ${tx.fee})
          </li>
        ))}
      </ul>
    </div>
  );
}

function TransactionForm({ formData, handleChange, submitTransaction }) {
  return (
    <form onSubmit={submitTransaction}>
      <input
        name="first_name"
        placeholder="First Name"
        value={formData.first_name}
        onChange={handleChange}
        required
      />
      <input
        name="last_name"
        placeholder="Last Name"
        value={formData.last_name}
        onChange={handleChange}
        required
      />
      <input
        name="fee"
        type="number"
        placeholder="Transaction Fee"
        value={formData.fee}
        onChange={handleChange}
        required
      />
      <button type="submit">Submit Transaction</button>
    </form>
  );
}

function SearchView({ searchQuery, setSearchQuery, handleSearch, results }) {
  return (
    <div>
      <h2>Search Transactions</h2>
      <form onSubmit={handleSearch}>
        <input
          placeholder="Search by Name"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>
      <ul>
        {results.map((tx, idx) => (
          <li key={idx}>
            {tx.form_data.first_name} {tx.form_data.last_name} (Fee: ${tx.fee})
          </li>
        ))}
      </ul>
    </div>
  );
}

function TotalFeesView({ totalFees }) {
  return (
    <div>
      <h2>Total Fees Collected</h2>
      <p>${totalFees}</p>
    </div>
  );
}

export default App;
