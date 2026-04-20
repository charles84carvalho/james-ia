# O Nascimento do James IA - Gestor Financeiro
import os

class JamesIA:
    def __init__(self):
        self.nome = "James"
        self.versao = "1.0.0 - Alpha"
        self.custo_fixo = 8000.00
        self.imposto = 0.05

    def status(self):
        return f"Saudações, senhor. Eu sou o {self.nome}. Meu sistema está online e já configurei o seu custo fixo de R$ {self.custo_fixo} e imposto de {self.imposto*100}%."

if __name__ == "__main__":
    mordomo = JamesIA()
    print(mordomo.status())
