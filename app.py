# -*- coding: utf-8 -*-
import streamlit as st
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Cotisation:
    base: float
    taux: float
    montant: float

def format_euro(montant: float) -> str:
    return f"{montant:,.2f} €".replace(",", " ")

def format_pourcentage(taux: float) -> str:
    return f"{taux * 100:.2f}%"

def calculer_cotisation(base: float, taux: float) -> float:
    return base * taux

def creer_section_cotisations(titre: str, cotisations: List[Tuple[str, float, float]], base_brut: float, base_csg: float, PMSS: float) -> Dict[str, Cotisation]:
    st.subheader(titre)
    resultat = {}
    
    for nom, base_defaut, taux_defaut in cotisations:
        st.write(f"\n{nom}")
        col1, col2 = st.columns(2)
        with col1:
            if base_defaut == "CSG":
                base = st.number_input(f"Base pour {nom}", value=base_csg, key=f"base_{titre}_{nom}")
            else:
                base = st.number_input(
                    f"Base pour {nom}", 
                    value=base_brut if base_defaut == 1.0 else min(base_brut, PMSS) if base_defaut == "PMSS" else base_brut * base_defaut,
                    key=f"base_{titre}_{nom}"
                )
        with col2:
            taux = st.number_input(
                f"Taux pour {nom} (%)", 
                value=taux_defaut * 100,
                key=f"taux_{titre}_{nom}"
            ) / 100
        
        montant = calculer_cotisation(base, taux)
        resultat[nom] = Cotisation(base, taux, montant)
    
    return resultat

def calculer_salaire():
    st.set_page_config(page_title="Calculateur de Salaire", layout="wide")
    st.title('Calculateur de Salaire')

    PMSS = st.number_input('PMSS (Plafond Mensuel Sécurité Sociale)', value=3666.00)

    col1, col2 = st.columns(2)
    with col1:
        heures = st.number_input('Heures mensuelles', value=151.67)
        taux = st.number_input('Taux horaire (€)', value=11.00)
        hs25 = st.number_input('Heures supp. 25%', value=0.0, step=0.5)
        hs50 = st.number_input('Heures supp. 50%', value=0.0, step=0.5)

    with col2:
        avantages = st.number_input('Avantages en nature (€)', value=0.0)
        primes = st.number_input('Primes (€)', value=0.0)

    salaire_base = heures * taux
    montant_hs25 = hs25 * taux * 1.25
    montant_hs50 = hs50 * taux * 1.50
    salaire_brut = salaire_base + montant_hs25 + montant_hs50 + avantages + primes
    base_csg_crds = salaire_brut * 0.9825

    with st.expander('Modifier les cotisations salariales'):
        cotisations_salariales = [
            ("Maladie", 1.0, 0.00),
            ("Vieillesse plafonnée", "PMSS", 0.069),
            ("Vieillesse déplafonnée", 1.0, 0.004),
            ("Chômage", 1.0, 0.00),
            ("Retraite complémentaire", 1.0, 0.040),
            ("Prévoyance", 1.0, 0.004),
            ("CSG déductible", "CSG", 0.067),
            ("CSG non déductible", "CSG", 0.024),
            ("CRDS", "CSG", 0.005)
        ]
        cotis_salariales = creer_section_cotisations(
            "Cotisations salariales",
            cotisations_salariales,
            salaire_brut,
            base_csg_crds,
            PMSS
        )

    st.subheader("Calcul de l'impôt")
    col_imp1, col_imp2 = st.columns(2)
    with col_imp1:
        revenu_imposable = st.number_input('Revenu imposable (€)', value=0.0)
    with col_imp2:
        taux_impot = st.number_input('Taux d\'imposition (%)', value=0.0)

    with st.expander('Modifier les cotisations patronales'):
        cotisations_patronales = [
            ("Maladie", 1.0, 0.130),
            ("Vieillesse plafonnée", "PMSS", 0.084),
            ("Vieillesse déplafonnée", 1.0, 0.019),
            ("Allocations familiales", 1.0, 0.0525),
            ("AT/MP", 1.0, 0.070),
            ("Chômage", 1.0, 0.0405),
            ("AGS", 1.0, 0.0015),
            ("Retraite complémentaire", 1.0, 0.060),
            ("Prévoyance", 1.0, 0.006),
            ("Formation professionnelle", 1.0, 0.010),
            ("Taxe d'apprentissage", 1.0, 0.0068),
            ("FNAL", 1.0, 0.001)
        ]
        cotis_patronales = creer_section_cotisations(
            "Cotisations patronales",
            cotisations_patronales,
            salaire_brut,
            base_csg_crds,
            PMSS
        )

    total_sal = sum(c.montant for c in cotis_salariales.values())
    total_pat = sum(c.montant for c in cotis_patronales.values())
    net_avant_impot = salaire_brut - total_sal
    impot = revenu_imposable * (taux_impot / 100)
    net_a_payer = net_avant_impot - impot
    cout_total = salaire_brut + total_pat

    st.header('Synthèse')
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric('Salaire brut', format_euro(salaire_brut))
    with col4:
        st.metric('Net avant impôt', format_euro(net_avant_impot))
    with col5:
        st.metric('Net à payer', format_euro(net_a_payer))

    with st.expander('Détail des calculs'):
        st.write("### 1. Salaire brut")
        st.write(f"Base ({heures}h × {format_euro(taux)}/h): {format_euro(salaire_base)}")
        if hs25 > 0:
            st.write(f"Heures sup. 25% ({hs25}h): {format_euro(montant_hs25)}")
            st.write(f"Calcul: {hs25}h × {format_euro(taux)}/h × 1.25 = {format_euro(montant_hs25)}")
        if hs50 > 0:
            st.write(f"Heures sup. 50% ({hs50}h): {format_euro(montant_hs50)}")
            st.write(f"Calcul: {hs50}h × {format_euro(taux)}/h × 1.50 = {format_euro(montant_hs50)}")
        if avantages > 0:
            st.write(f"Avantages: {format_euro(avantages)}")
        if primes > 0:
            st.write(f"Primes: {format_euro(primes)}")
        st.write(f"**Total brut: {format_euro(salaire_brut)}**")

        st.write("\n### 2. Cotisations")
        st.write("#### Autres cotisations salariales")
        for nom, cotis in cotis_salariales.items():
            if nom not in ["CSG déductible", "CSG non déductible", "CRDS"]:
                st.write(f"{nom}:")
                st.write(f"  Base: {format_euro(cotis.base)}")
                st.write(f"  × Taux: {format_pourcentage(cotis.taux)}")
                st.write(f"  = Montant: {format_euro(cotis.montant)}")

        st.write("\n#### Calcul de la base CSG-CRDS")
        st.write("La CSG et la CRDS sont calculées sur une base de 98.25% du salaire brut")
        st.write(f"Base CSG-CRDS = Salaire brut × 98.25%")
        st.write(f"Base CSG-CRDS = {format_euro(salaire_brut)} × 98.25%")
        st.write(f"Base CSG-CRDS = {format_euro(base_csg_crds)}")
        
        st.write("\nCalcul des CSG et CRDS :")
        for nom, cotis in cotis_salariales.items():
            if nom in ["CSG déductible", "CSG non déductible", "CRDS"]:
                st.write(f"{nom}:")
                st.write(f"  Base: {format_euro(cotis.base)}")
                st.write(f"  × Taux: {format_pourcentage(cotis.taux)}")
                st.write(f"  = Montant: {format_euro(cotis.montant)}")
        
        st.write(f"\n**Total des cotisations salariales: {format_euro(total_sal)}**")

        st.write("\n#### Cotisations patronales")
        for nom, cotis in cotis_patronales.items():
            st.write(f"{nom}:")
            st.write(f"  Base: {format_euro(cotis.base)}")
            st.write(f"  × Taux: {format_pourcentage(cotis.taux)}")
            st.write(f"  = Montant: {format_euro(cotis.montant)}")
        st.write(f"**Total des cotisations patronales: {format_euro(total_pat)}**")

        st.write("\n### 3. Calcul du net")
        st.write(f"Salaire brut: {format_euro(salaire_brut)}")
        st.write(f"- Total des cotisations salariales: {format_euro(total_sal)}")
        st.write(f"= Net avant impôt: {format_euro(net_avant_impot)}")
        st.write(f"- Impôt sur le revenu ({taux_impot}% de {format_euro(revenu_imposable)})")
        st.write(f"  {format_euro(revenu_imposable)} × {taux_impot}% = {format_euro(impot)}")
        st.write(f"= **Net à payer: {format_euro(net_a_payer)}**")
        st.write(f"\nCoût total employeur: {format_euro(cout_total)}")

if __name__ == '__main__':
    calculer_salaire()