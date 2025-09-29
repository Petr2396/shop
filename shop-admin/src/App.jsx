import React from "react";
import { Admin, Resource } from "react-admin";
import simpleRestProvider from "ra-data-simple-rest";
import { ProductList } from "./products";

export default function App() {
  return (
    <Admin dataProvider={simpleRestProvider("http://localhost:5000/api")}> 
      <Resource name="products" list={ProductList} />
    </Admin>
  );
}
