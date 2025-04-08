import React, { useState } from 'react';

const TestPage: React.FC = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>測試頁面</h1>
      <p>計數器: {count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
};

export default TestPage; 