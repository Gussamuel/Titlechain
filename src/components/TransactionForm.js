import React from 'react';

function TransactionForm({ formData, handleChange, submitTransaction }) {
  return (
    <form onSubmit={submitTransaction}>
      <input
        type="text"
        name="first_name"
        placeholder="First Name"
        value={formData.first_name}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="last_name"
        placeholder="Last Name"
        value={formData.last_name}
        onChange={handleChange}
        required
      />
      <input
        type="number"
        name="fee"
        placeholder="Transaction Fee"
        value={formData.fee}
        onChange={handleChange}
        required
      />
      <button type="submit">Submit Transaction</button>
    </form>
  );
}

export default TransactionForm;
