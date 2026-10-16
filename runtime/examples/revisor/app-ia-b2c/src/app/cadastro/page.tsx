// Formulário sintético de cadastro: só nomes de campos.
export default function Cadastro() {
  const campos = ["fullName", "email", "phoneNumber", "cpf", "birthDate"];
  return <form>{campos.map((c) => <input key={c} name={c} />)}</form>;
}
