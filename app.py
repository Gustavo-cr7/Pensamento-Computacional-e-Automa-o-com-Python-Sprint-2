from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import random

def energia_disponivel(capacidade, consumo):
    valor = capacidade - consumo
    if valor < 0:
        return 0
    return valor

def peso(prioridade):
    if prioridade == "alta":
        return 3
    if prioridade == "media":
        return 2
    return 1

def criar_veiculos(qtd):
    lista = []
    for i in range(qtd):
        lista.append({
            "veiculo": "EV-" + str(i + 1),
            "bateria": random.randint(10, 80),
            "prioridade": random.choice(["baixa", "media", "alta"]),
            "protocolo": random.choice(["OCPP 1.6", "OCPP 2.0.1", "Proprietario"])
        })
    return lista

def distribuir(lista, energia):
    total_peso = 0
    for item in lista:
        total_peso += peso(item["prioridade"])

    for item in lista:
        if energia == 0 or total_peso == 0:
            item["potencia"] = 0
        else:
            item["potencia"] = round(energia * peso(item["prioridade"]) / total_peso, 2)
    return lista

def cobrar(lista, preco, horas):
    for item in lista:
        item["kwh"] = round(item["potencia"] * horas, 2)
        item["valor"] = round(item["kwh"] * preco, 2)
    return lista

def integrar(lista):
    for item in lista:
        if "OCPP" in item["protocolo"]:
            item["integracao"] = "compativel"
        else:
            item["integracao"] = "risco"
    return lista

def analisar(lista, capacidade, consumo, energia):
    texto = []
    uso = consumo / capacidade
    riscos = 0
    total = 0
    potencia_total = 0

    for item in lista:
        total += item["valor"]
        potencia_total += item["potencia"]
        if item["integracao"] == "risco":
            riscos += 1

    media = potencia_total / len(lista)

    if uso >= 0.85:
        texto.append("Risco de sobrecarga alto. O consumo do predio esta muito proximo da capacidade da rede.")
    elif uso >= 0.65:
        texto.append("Risco de sobrecarga medio. O sistema deve controlar melhor os horarios de pico.")
    else:
        texto.append("Risco de sobrecarga baixo. A rede ainda possui margem operacional.")

    if energia == 0:
        texto.append("Nao existe energia disponivel para carregamento.")
    elif media < 7:
        texto.append("A potencia media por veiculo esta baixa. O tempo de recarga pode ser alto.")
    else:
        texto.append("A distribuicao de energia esta adequada para o cenario atual.")

    if riscos > 0:
        texto.append("Existe risco de interoperabilidade. Alguns carregadores usam protocolo proprietario.")
    else:
        texto.append("Todos os carregadores usam protocolos abertos compativeis.")

    texto.append("A receita estimada da simulacao e R$ " + str(round(total, 2)) + ".")

    if len(lista) >= 15 and energia < 100:
        texto.append("Melhoria recomendada: limitar novas conexoes ou priorizar usuarios com maior urgencia.")
    else:
        texto.append("Melhoria recomendada: manter balanceamento dinamico e monitorar horarios de maior demanda.")

    return texto

def pagina(capacidade, consumo, qtd, preco, horas):
    energia = energia_disponivel(capacidade, consumo)
    lista = criar_veiculos(qtd)
    lista = distribuir(lista, energia)
    lista = cobrar(lista, preco, horas)
    lista = integrar(lista)
    analise = analisar(lista, capacidade, consumo, energia)

    total_kwh = 0
    total_valor = 0
    compativeis = 0
    riscos = 0

    for item in lista:
        total_kwh += item["kwh"]
        total_valor += item["valor"]
        if item["integracao"] == "compativel":
            compativeis += 1
        else:
            riscos += 1

    linhas = ""
    for item in lista:
        linhas += f"""
        <tr>
            <td>{item["veiculo"]}</td>
            <td>{item["bateria"]}%</td>
            <td>{item["prioridade"]}</td>
            <td>{item["protocolo"]}</td>
            <td>{item["integracao"]}</td>
            <td>{item["potencia"]}</td>
            <td>{item["kwh"]}</td>
            <td>R$ {item["valor"]}</td>
        </tr>
        """

    analise_html = ""
    for item in analise:
        analise_html += "<li>" + item + "</li>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ChargeGrid</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f4f4f4;
            }}
            h1, h2 {{
                color: #222;
            }}
            .card {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 0 8px #ccc;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
            }}
            .box {{
                background: #ffffff;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 0 8px #ccc;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background: #222;
                color: white;
            }}
            input {{
                padding: 8px;
                margin: 5px;
                width: 150px;
            }}
            button {{
                padding: 10px 20px;
                background: #222;
                color: white;
                border: none;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <h1>ChargeGrid Intelligence</h1>
        <div class="card">
            <form method="get">
                <label>Capacidade da rede em kW</label>
                <input name="capacidade" type="number" value="{capacidade}">
                <label>Consumo do predio em kW</label>
                <input name="consumo" type="number" value="{consumo}">
                <label>Quantidade de veiculos</label>
                <input name="qtd" type="number" value="{qtd}">
                <label>Preco por kWh</label>
                <input name="preco" type="number" step="0.1" value="{preco}">
                <label>Horas de recarga</label>
                <input name="horas" type="number" step="0.5" value="{horas}">
                <button type="submit">Simular</button>
            </form>
        </div>

        <div class="grid">
            <div class="box"><h3>Capacidade</h3><p>{capacidade} kW</p></div>
            <div class="box"><h3>Consumo</h3><p>{consumo} kW</p></div>
            <div class="box"><h3>Energia disponivel</h3><p>{energia} kW</p></div>
            <div class="box"><h3>Veiculos</h3><p>{qtd}</p></div>
        </div>

        <div class="card">
            <h2>Resumo financeiro</h2>
            <p>Energia total: {round(total_kwh, 2)} kWh</p>
            <p>Valor total: R$ {round(total_valor, 2)}</p>
        </div>

        <div class="card">
            <h2>Interoperabilidade</h2>
            <p>Compativeis: {compativeis}</p>
            <p>Com risco: {riscos}</p>
        </div>

        <div class="card">
            <h2>Analise por IA </h2>
            <ul>{analise_html}</ul>
        </div>

        <div class="card">
            <h2>Simulacao dos carregadores</h2>
            <table>
                <tr>
                    <th>Veiculo</th>
                    <th>Bateria</th>
                    <th>Prioridade</th>
                    <th>Protocolo</th>
                    <th>Integracao</th>
                    <th>Potencia kW</th>
                    <th>Energia kWh</th>
                    <th>Valor</th>
                </tr>
                {linhas}
            </table>
        </div>
    </body>
    </html>
    """

class Servidor(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)

        capacidade = int(query.get("capacidade", [300])[0])
        consumo = int(query.get("consumo", [120])[0])
        qtd = int(query.get("qtd", [10])[0])
        preco = float(query.get("preco", [1.5])[0])
        horas = float(query.get("horas", [2])[0])

        html = pagina(capacidade, consumo, qtd, preco, horas)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

if __name__ == "__main__":
    servidor = HTTPServer(("localhost", 8000), Servidor)
    print("Servidor iniciado.")
    print("Abra no navegador: http://localhost:8000")
    servidor.serve_forever()
