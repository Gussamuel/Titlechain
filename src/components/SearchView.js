import React from 'react';

function SearchView({ searchQuery, setSearchQuery, handleSearch, results }) {
  return (
    <div>
      <h2>Search Transactions</h2>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search by Name"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          required
        />
        <button type="submit">Search</button>
      </form>

      <ul>
        {results.map((tx, idx) => (
          <li key={idx}>
            <strong>Name:</strong> {tx.form_data.first_name} {tx.form_data.last_name}<br />
            <strong>Fee:</strong> ${tx.fee}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SearchView;
