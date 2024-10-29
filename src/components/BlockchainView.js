import React from 'react';
import './BlockchainView.css'; // Import the CSS for styling

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
                <p><strong>Name:</strong> {tx.form_data.first_name} {tx.form_data.last_name}</p>
                <p><strong>Fee:</strong> ${tx.fee}</p>
              </div>
            ))}
          </div>

          {/* Render an arrow to the next block if not the last block */}
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

export default BlockchainView;
