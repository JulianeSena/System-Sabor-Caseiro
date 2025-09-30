
# Rotas

| Endpoint | Método | Proteção | Corpo (Body) | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `/admin/login` | `POST` | Nenhuma | `{ "nome": "...", "senha": "..." }` | Realiza o login de um administrador. |
| `/login/cliente` | `POST` | Nenhuma | `{ "documento": "...", "senha": "..." }` | Realiza o login de um cliente. |
| `/logout` | `POST` | Login Requerido | Nenhum | Invalida o token de acesso (logout). |
| `/cadastro` | `POST` | Admin | `{ "nome": "...", "email": "...", "telefone": "...", "documento": "...", "senha": "...", "role": "..." }` | Cadastra um novo usuário (cliente, gerente, ou admin). |
| `/cliente/buscar` | `POST` | Admin | `{ "documento": "..." }` | Busca um cliente pelo número do documento. |
| `/cliente/<id>` | `GET` | Login Requerido | Nenhum | Retorna os dados de um cliente. Admin/Gerente pode ver qualquer um, cliente só pode ver a si mesmo. |
| `/cliente/<id>` | `PUT` | Login Requerido | `{ "nome": "...", "email": "...", "telefone": "...", "senha": "..." }` | Atualiza os dados de um cliente. Admin/Gerente pode editar qualquer um, cliente só pode editar a si mesmo. |
| `/cliente/<id>` | `DELETE` | Admin | Nenhum | Deleta um usuário. |
| `/cliente/<id>/cupons` | `GET` | Login Requerido | Nenhum | Retorna todos os cupons de um cliente específico. (Rota a ser implementada) |
