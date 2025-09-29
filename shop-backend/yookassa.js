const YooKassa = require("yookassa");
require("dotenv").config();

const yooKassa = new YooKassa({
  shopId: process.env.YOOKASSA_SHOP_ID,
  secretKey: process.env.YOOKASSA_SECRET,
});

async function createPayment(amount, description) {
  const response = await yooKassa.createPayment({
    amount: {
      value: amount,
      currency: "RUB",
    },
    confirmation: {
      type: "redirect",
      return_url: "http://localhost:5173/success",
    },
    capture: true,
    description,
  });

  return response;
}

module.exports = {
  createPayment,
};