📱 Sabor Caseiro - Gerenciador de Cartão de Promoções
Um aplicativo móvel para gerenciar e aproveitar promoções de forma inteligente através de um cartão digital único.

✨ Funcionalidades Principais
🎯 Cartão Digital Único - Um único cartão para acessar múltiplas promoções

📊 Gestão de Promoções - Visualize e organize todas as ofertas disponíveis

🔔 Notificações Personalizadas - Alertas sobre novas promoções e ofertas relâmpago

🛠️ Tecnologias Utilizadas



| Endpoint | Método | Proteção | Corpo (Body) | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `/admin/login` | `POST` | Nenhuma | Credenciais de admin | Realiza o login de um administrador. |
| `/login/cliente` | `POST` | Nenhuma | Credenciais de cliente | Realiza o login de um cliente. |
| `/cadastro` | `POST` | **Admin** | Dados do novo usuário | Cadastra um novo usuário (cliente ou admin). |
| `/cliente/<id>` | `GET` | **Login Requerido** | Nenhum | Admin vê qualquer um; cliente só vê a si mesmo. |
| `/cliente/<id>` | `DELETE` | **Admin** | Nenhum | Deleta um usuário. |
| `/logout` | `POST` | **Login Requerido** | Nenhum | Invalida o token de acesso (logout). |
