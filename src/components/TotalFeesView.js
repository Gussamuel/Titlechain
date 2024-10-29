import React from 'react';

function TotalFeesView({ totalFees }) {
  return (
    <div>
      <h2>Total Fees Collected</h2>
      <p>${totalFees}</p>
    </div>
  );
}

export default TotalFeesView;
