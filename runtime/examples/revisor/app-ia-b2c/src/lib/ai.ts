import OpenAI from "openai";
const client = new OpenAI();
export async function responder(pergunta: string) {
  const r = await client.chat.completions.create({ model: "modelo-exemplo", messages: [{ role: "user", content: pergunta }] });
  return r.choices[0].message.content;
}
