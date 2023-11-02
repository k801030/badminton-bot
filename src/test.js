const now = new Date().toISOString();
console.log(now);

console.log(new Date(now).getHours());

console.log(new Date("2023-11-02T05:52:53.253540").getHours());
console.log(new Date("2023-11-02T05:52:53.253548-04:00").getHours());