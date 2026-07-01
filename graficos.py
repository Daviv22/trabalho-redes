import json
import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# MAPA SONDAS → PAÍSES
# ==========================================

PROBES = {
    1016001: "Africa do Sul",
    1013145: "Chile",
    18275: "Estados Unidos",
    1015514: "Brasil",
    1008990: "Japao",
    22311: "Portugal",
    1012769: "Equador",
    1010208: "Portugal",
    1014739: "Franca",
    64976: "Nigeria",
    61615: "Taiwan",
    1015995: "Italia",
    62412: "Franca",
    1013071: "Brasil",
    1011667: "Africa do Sul",
    18357: "Chile",
    1002598: "Portugal",
    53335: "Brasil",
    51131: "Canada",
    1011902: "Filipinas",
    64625: "Taiwan",
    1005929: "Quenia"
}

# ==========================================
# CONTINENTES
# ==========================================

CONTINENTES = {
    "Brasil": "America do Sul",
    "Chile": "America do Sul",
    "Equador": "America do Sul",

    "Estados Unidos": "America do Norte",
    "Canada": "America do Norte",

    "Franca": "Europa",
    "Italia": "Europa",
    "Portugal": "Europa",

    "Nigeria": "Africa",
    "Quenia": "Africa",
    "Africa do Sul": "Africa",

    "Japao": "Asia",
    "Taiwan": "Asia",
    "Filipinas": "Asia"
}

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def carregar_json(arquivo):
    dados = []
    with open(arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                try:
                    dados.append(json.loads(linha))
                except:
                    pass
    return dados


def identificar_site(dst):
    dst = str(dst).lower()
    if "cnn" in dst:
        return "cnn.com"
    elif "ft" in dst:
        return "ft.com"
    elif "apnews" in dst:
        return "apnews.com"
    return None


def obter_latencia(reg):
    try:
        hops = reg.get("result", [])
        ultimo = hops[-1]
        rtts = [
            t["rtt"]
            for t in ultimo.get("result", [])
            if isinstance(t, dict) and "rtt" in t
        ]
        return sum(rtts) / len(rtts) if rtts else None
    except:
        return None


# ==========================================
# PROCESSAMENTO
# ==========================================

dados = []

for arquivo in os.listdir("."):
    if not arquivo.endswith(".json"):
        continue

    registros = carregar_json(arquivo)

    for reg in registros:

        probe = reg.get("prb_id")
        if probe not in PROBES:
            continue

        pais = PROBES[probe]
        continente = CONTINENTES.get(pais, "Outros")

        site = identificar_site(reg.get("dst_name"))
        if site is None:
            continue

        protocolo = "IPv6" if reg.get("af") == 6 else "IPv4"

        lat = obter_latencia(reg)
        if lat is None:
            continue

        timestamp = reg.get("timestamp")
        if timestamp is None:
            continue

        dados.append({
            "tempo": pd.to_datetime(timestamp, unit="s"),
            "pais": pais,
            "continente": continente,
            "site": site,
            "ip": protocolo,
            "latencia": lat
        })

df = pd.DataFrame(dados)

print("Total de registros:", len(df))

# ==========================================
# PRÉ-PROCESSAMENTO 1H
# ==========================================

df = df.sort_values("tempo")
df["hora"] = df["tempo"].dt.floor("h")

os.makedirs("graficos", exist_ok=True)

# ==========================================
# FUNÇÃO DE GRÁFICO FINAL
# ==========================================

def plot_cont_site(df_base, continente, site):

    plt.figure(figsize=(13,6))

    df_filtro = df_base[
        (df_base["continente"] == continente) &
        (df_base["site"] == site)
    ]

    if df_filtro.empty:
        plt.close()
        return

    for (pais, ip), grupo in df_filtro.groupby(["pais", "ip"]):

        grupo = (
            grupo.groupby("hora")["latencia"]
            .mean()
            .reset_index()
            .sort_values("hora")
        )

        estilo = "--" if ip == "IPv6" else "-"

        plt.plot(
            grupo["hora"],
            grupo["latencia"],
            label=f"{pais} - {ip}",
            linestyle=estilo,
            linewidth=1.6,
            alpha=0.9
        )

    plt.title(f"{continente} - {site}")
    plt.xlabel("Tempo (1h média)")
    plt.ylabel("Latência (ms)")
    plt.legend()
    plt.grid(True)

    nome = f"graficos/{continente}_{site}.png".replace(" ", "_")
    plt.savefig(nome, bbox_inches="tight")
    plt.close()


# ==========================================
# GERAR GRÁFICOS (5 POR DESTINO AUTOMÁTICO)
# ==========================================

for site in df["site"].unique():
    for continente in df["continente"].unique():

        plot_cont_site(df, continente, site)

print("\nGráficos gerados com sucesso")