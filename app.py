import os
import random
from datetime import datetime
from IPython.display import display, Markdown, clear_output, FileLink
import ipywidgets as widgets
import openai

# Widget para inserir a chave da API do OpenAI
api_key_widget = widgets.Password(description='API Key:', layout=widgets.Layout(width='auto'))
display(api_key_widget)

# Definir a chave da API do OpenAI após o usuário inserir a chave
def configurar_api_key(change):
    openai.api_key = api_key_widget.value

api_key_widget.observe(configurar_api_key, names='value')

TEMAS = [
    "bom dia", "boa tarde", "boa noite", "amor", "ódio", "reflexão", "motivação"
]

ultimas_frases = {}

def gerar_frase_openai(tema):
    prompt = f"Crie uma frase marcante sobre {tema}. Seja original e inspirador."
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.9
        )
        frase = resposta.choices[0].message.content.strip()
        return frase
    except Exception as e:
        return f"Erro ao gerar frase: {e}"

def salvar_frase_em_arquivo(tema, frase):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    nome_arquivo = f"frases/frase_{tema.replace(' ', '_')}_{timestamp}.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"Tema: {tema}\n\n{frase}")
    return nome_arquivo

def configurar_interface():
    os.makedirs("frases", exist_ok=True)
    menu = widgets.Dropdown(
        options=TEMAS,
        description='Tema:',
        style={'description_width': 'initial'}
    )
    botao = widgets.Button(
        description="Gerar Frase",
        button_style='primary'
    )
    saida = widgets.Output()

    def ao_clicar(b):
        with saida:
            clear_output()
            tema = menu.value
            frase = gerar_frase_openai(tema)
            display(Markdown(f"### Frase sobre *{tema}*\n\n{frase}"))
            caminho = salvar_frase_em_arquivo(tema, frase)
            display(FileLink(caminho, result_html_prefix="📎 Download: "))

    botao.on_click(ao_clicar)
    display(menu, botao, saida)

configurar_interface()
