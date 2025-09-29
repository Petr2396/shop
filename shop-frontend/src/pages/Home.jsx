import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:5000/api/products").then((res) => setProducts(res.data));
  }, []);

  return (
   
    <div className="grid grid-cols-2 gap-4 p-4">
      {products.map((p) => (
        <div key={p.id} className="border p-4 rounded-xl shadow">
          <h2 className="text-lg font-bold">{p.name}</h2>
          <p>{p.price} ₽</p>
        </div>
      ))}
    </div>
  );
}
