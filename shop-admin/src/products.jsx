import React from "react";
import { List, Datagrid, TextField, NumberField } from "react-admin";

export const ProductList = (props) => (
  <List {...props}>
    <Datagrid>
      <TextField source="id" />
      <TextField source="name" />
      <NumberField source="price" />
    </Datagrid>
  </List>
);





