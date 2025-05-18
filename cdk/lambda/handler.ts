export const handler = async () => {
  console.log("EventBridge triggered Lambda!");
  return { statusCode: 200, body: "Success" };
};
