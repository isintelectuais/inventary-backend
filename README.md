# 📦 Sistema de Inventário de Armazém

Este repositório contém o **backend** do sistema de inventário de um armazém, desenvolvido com **Django**, **Django Ninja** e **SQLite**. O sistema está em desenvolvimento contínuo e tem como objetivo gerenciar de forma eficiente os recursos, produtos, robôs e agendamentos de um armazém.

> 🚧 Projeto em atualização e fase de testes  
> 👩‍💻 Desenvolvido por uma única pessoa, responsável por DevOps, backend, testes e banco de dados.

---

## 📚 Sumário

- [📦 Visão Geral](#-visão-geral)
- [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🚀 Como Executar](#-como-executar)
- [🔌 Rotas e APIs](#-rotas-e-apis)
- [🧪 Testes](#-testes)
- [📌 Status do Projeto](#-status-do-projeto)
- [👩‍💻 Autoria](#-autoria)

---

## 📦 Visão Geral

O sistema foi desenvolvido para gerenciar de forma modular e escalável os seguintes aspectos de um armazém automatizado:

- Cadastro e autenticação de usuários
- Controle de inventário de produtos
- Agendamento de tarefas
- Gerenciamento de robôs e suas trajetórias
- Armazenamento de imagens e logs de erros
- Organização de armazéns físicos e virtuais

---

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Django**
- **Django Ninja** – APIs REST rápidas e tipadas
- **SQLite** – Banco de dados leve e embutido
- **(Em breve)** Docker para containerização

---

## 📁 Estrutura do Projeto

```
sistema_sia/
├── manage.py
├── sistema_inventario/
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── apps/
    ├── usuarios/
    ├── inventario/
    ├── agendamento/
    ├── robos/
    ├── trajetorias/
    ├── logs_erros/
    ├── imagens/
    └── armazens/
```

---

## 🚀 Como Executar

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
```

2. **Crie e ative um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate       # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Execute as migrações**

```bash
python manage.py migrate
```

5. **Inicie o servidor**

```bash
python manage.py runserver
```

6. **Acesse no navegador**

- Admin: `http://127.0.0.1:8000/admin/`
- API Docs: `http://127.0.0.1:8000/api/docs`

---

## 🔌 Rotas e APIs

As APIs foram construídas com **Django Ninja**, com documentação interativa em `/api/docs`.

### Apps e possíveis rotas:

- `usuarios/` → Autenticação, cadastro, perfil
- `inventario/` → Produtos, estoque
- `agendamento/` → Agendamento de tarefas
- `robos/` → Robôs disponíveis
- `trajetorias/` → Rotas e caminhos definidos
- `logs_erros/` → Registro de falhas
- `imagens/` → Upload e visualização
- `armazens/` → Gestão dos armazéns

> ⚠️ As rotas específicas estão sendo testadas e documentadas gradualmente conforme o projeto evolui.

---

## 🧪 Testes

Os testes estão sendo implementados com o framework nativo do Django:

```bash
python manage.py test
```

---

## 📌 Status do Projeto

- [x] Estrutura inicial do projeto
- [x] Criação dos apps principais
- [x] Implementação de rotas com Django Ninja
- [x] Autenticação de usuários
- [ ] Testes automatizados
- [ ] Dockerização
- [ ] Integração com frontend

---

## 👩‍💻 Autoria

Desenvolvido por **Andressa Silva** – responsável por backend, banco de dados, testes e DevOps.

- GitHub: [@AndressaSilva0](https://github.com/AndressaSilva0)
- Email: andressasp68@gmail.com
- LinkedIn: [linkedin.com/in/andressa-silva-29430a218/](https://linkedin.com/in/andressa-silva-29430a218/)
