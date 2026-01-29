import sys
sys.path.append(".")  # Adiciona o diretório atual ao path para garantir que o Python encontre o módulo 'app'

from sqlmodel import Session, select
from app.models import User, Snippet, Tag, Task, SnippetCollaboratorLink, SnippetTagLink
from main import engine, pwd_context


def seed_database():
    with Session(engine) as session:
        # 1. Verifica se já existem dados para evitar duplicidade
        if session.exec(select(User)).first():
            print("⚠️  O banco de dados já contém dados. Seed cancelado.")
            return

        print("🌱 Iniciando o seed do banco de dados...")

        password_bruno = pwd_context.hash("senhak")  # Senha: senhak
        password_alice = pwd_context.hash("alice123") # Senha: alice123
        
        user_bruno = User(username="bruno", email="bruno@email.com", hashed_password=password_bruno)
        user_alice = User(username="alice", email="alice@work.com", hashed_password=password_alice)
        
        session.add(user_bruno)
        session.add(user_alice)
        session.commit()  # Commit para gerar os IDs
        
        session.refresh(user_bruno)
        session.refresh(user_alice)
        print(f"✅ Usuários criados: {user_bruno.username}, {user_alice.username}")

        tag_awaiting_art = Tag(name="Aguardando", value="Arte")
        tag_awaiting_review = Tag(name="Aguardando", value="Revisão")
        tag_urgent = Tag(name="Urgente")
        
        session.add_all([tag_awaiting_art, tag_awaiting_review, tag_urgent])
        session.commit()
        
        session.refresh(tag_awaiting_review)
        session.refresh(tag_urgent)
        print("✅ Tags criadas.")


        # --- Snippet 1: Simples (Bruno) ---
        snip1 = Snippet(
            title="Ideias para o SnippetFlow",
            body="Preciso focar na performance e na simplicidade. Usar HTMX foi uma boa escolha.",
            author_id=user_bruno.id
        )
        session.add(snip1)

        # --- Snippet 2: Com Tasks e Tags (Bruno) ---
        snip2 = Snippet(
            title="Lista de Compras da Semana",
            body="Coisas para comprar no mercado para o escritório.",
            author_id=user_bruno.id
        )
        session.add(snip2)
        session.commit()

        session.refresh(snip2)  # Adicionar Tasks ao Snip2
        task1 = Task(text="Comprar Café Premium", completed=False, snippet_id=snip2.id)
        task2 = Task(text="Filtro de papel", completed=True, snippet_id=snip2.id)
        task3 = Task(text="Leite", completed=False, snippet_id=snip2.id)
        session.add_all([task1, task2, task3])

        # Adicionando Link de Tags ao Snip2 (Usando a tabela de link explicitamente ou a lista do SQLModel)
        # SQLModel permite adicionar direto na lista se configurado corretamente, 
        # mas vamos criar os links manuais para garantir
        link_tag1 = SnippetTagLink(snippet_id=snip2.id, tag_id=tag_awaiting_review.id)
        link_tag2 = SnippetTagLink(snippet_id=snip2.id, tag_id=tag_urgent.id)
        session.add_all([link_tag1, link_tag2])


        # --- Snippet 3: Colaborativo (Autor: Alice, Colab: Bruno) ---
        snip3 = Snippet(
            title="Documentação da API",
            body="Estrutura inicial dos endpoints do backend em FastAPI.",
            author_id=user_alice.id
        )
        session.add(snip3)
        session.commit()
        session.refresh(snip3)

        # Bruno colabora no snippet da Alice como 'reviewer'
        colab_link = SnippetCollaboratorLink(
            snippet_id=snip3.id, 
            user_id=user_bruno.id, 
            role="revisor"
        )
        session.add(colab_link)
        
        # Tags no Snip3
        link_tag3 = SnippetTagLink(snippet_id=snip3.id, tag_id=tag_urgent.id)
        session.add_all([link_tag3]) #, link_tag4])

        # ---------------------------------------------------------
        # 4. FINALIZAR
        # ---------------------------------------------------------
        session.commit()
        print("🚀 Banco de dados populado com sucesso!")
    # / with Session(engine) as session


if __name__ == "__main__":
    seed_database()
