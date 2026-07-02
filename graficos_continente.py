import json
import os
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# MAPA SONDAS → PAÍSES
# =====================================================

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
    1005929: "Quenia",
    1016141: "Mexico"
}

# =====================================================
# CONTINENTES
# =====================================================

CONTINENTES = {
    "Brasil": "America do Sul",
    "Chile": "America do Sul",
    "Equador": "America do Sul",

    "Estados Unidos": "America do Norte",
    "Canada": "America do Norte",
    "Mexico": "America do Norte",

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

# =====================================================
# LEITURA
# =====================================================

def carregar_json(arquivo):
    dados = []

    with open(arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()

            if not linha:
                continue

            try:
                dados.append(json.loads(linha))
            except:
                pass

    return dados


# =====================================================
# IDENTIFICA DESTINO
# =====================================================

def identificar_site(dst):

    dst = str(dst).lower()

    if "cnn" in dst:
        return "cnn.com"

    if "ft" in dst:
        return "ft.com"

    if "apnews" in dst:
        return "apnews.com"

    return None


# =====================================================
# LATÊNCIA
# =====================================================

def obter_latencia(reg):

    try:

        ultimo = reg["result"][-1]

        rtts = [
            r["rtt"]
            for r in ultimo["result"]
            if isinstance(r, dict) and "rtt" in r
        ]

        if not rtts:
            return None

        return sum(rtts) / len(rtts)

    except:
        return None


# =====================================================
# SALTOS
# =====================================================

def obter_saltos(reg):

    try:

        if not reg.get("destination_ip_responded", False):
            return None

        return reg["result"][-1]["hop"]

    except:
        return None


# =====================================================
# PROCESSAMENTO
# =====================================================

dados = []

for arquivo in os.listdir("."):

    if not arquivo.endswith(".json"):
        continue

    print("Lendo", arquivo)

    registros = carregar_json(arquivo)

    for reg in registros:

        probe = reg.get("prb_id")

        if probe not in PROBES:
            continue

        site = identificar_site(reg.get("dst_name"))

        if site is None:
            continue

        latencia = obter_latencia(reg)
        saltos = obter_saltos(reg)

        if latencia is None or saltos is None:
            continue

        pais = PROBES[probe]
        continente = CONTINENTES[pais]

        dados.append({

            "tempo": pd.to_datetime(reg["timestamp"], unit="s"),

            "hora": pd.to_datetime(reg["timestamp"], unit="s").floor("h"),

            "pais": pais,

            "continente": continente,

            "site": site,

            "ip": "IPv6" if reg["af"] == 6 else "IPv4",

            "latencia": latencia,

            "saltos": saltos
        })

df = pd.DataFrame(dados)

print()
print("Registros válidos:", len(df))

# =====================================================
# PASTAS
# =====================================================

os.makedirs("continentes/graficos_latencia", exist_ok=True)
os.makedirs("continentes/graficos_saltos", exist_ok=True)

# =====================================================
# FUNÇÃO 
# =====================================================

def plotar(df, site, continente, coluna, ylabel, pasta):

    filtro = df[(df["site"] == site) & (df["continente"] == continente)]

    if filtro.empty:
        return

    plt.figure(figsize=(13, 6))


    for ip, grupo in filtro.groupby("ip"):

        # média por hora, apenas do continente/site selecionado
        serie = (
            grupo
            .groupby("hora")[coluna]
            .mean()
            .reset_index()
            .sort_values("hora")
        )

        plt.plot(
            serie["hora"],
            serie[coluna],
            label=ip,
            linestyle="--" if ip == "IPv6" else "-",
            linewidth=2
        )

    titulo = (
        "Latência Média"
        if coluna == "latencia"
        else "Quantidade Média de Saltos"
    )

    plt.title(f"{titulo} - {continente} - {site}")

    plt.xlabel("Tempo (média de 1 hora)")
    plt.ylabel(ylabel)

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    nome = os.path.join(
        pasta,
        f"{continente.replace(' ', '_')}_{site.replace('.', '_')}.png"
    )

    plt.savefig(nome, dpi=150)
    plt.close()


# =====================================================
# GERA OS GRÁFICOS
# =====================================================

sites = sorted(df.site.unique())
continentes = sorted(df.continente.unique())

total_latencia = 0
total_saltos = 0

for site in sites:

    for continente in continentes:

        # latência
        plotar(
            df,
            site,
            continente,
            "latencia",
            "Latência (ms)",
            "continentes/graficos_latencia"
        )

        # saltos
        plotar(
            df,
            site,
            continente,
            "saltos",
            "Quantidade de Saltos",
            "continentes/graficos_saltos"
        )

print()
print("===================================")
print(f"Sites: {len(sites)} | Continentes: {len(continentes)}")
print("Gráficos de latência gerados (um por continente x site).")
print("Gráficos de saltos gerados (um por continente x site).")
print("===================================")