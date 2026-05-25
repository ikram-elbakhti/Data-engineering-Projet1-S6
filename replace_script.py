import re

with open('mexora_etl/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Page 1
old1 = '''                st.dataframe(
                    df_geo.rename(columns={'region_admin': 'Région', 'zone_geo': 'Zone', 'ca': 'CA (DH)', 'volume': 'Volume'}),
                    column_config={
                        "CA (DH)": st.column_config.NumberColumn(format="%.0f DH"),
                        "Volume": st.column_config.NumberColumn(format="%d u")
                    },
                    hide_index=True,
                    use_container_width=True
                )'''
new1 = '''                df_fmt = df_geo.rename(columns={'region_admin': 'Région', 'zone_geo': 'Zone', 'ca': 'CA (DH)', 'volume': 'Volume'})
                df_fmt['CA (DH)'] = df_fmt['CA (DH)'].apply(lambda x: f"{x:,.0f} DH".replace(',', ' '))
                df_fmt['Volume'] = df_fmt['Volume'].apply(lambda x: f"{x} u")
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)'''
content = content.replace(old1, new1)

# 2. Page 2
old2 = '''                st.dataframe(
                    df_top10.rename(columns={'nom_produit': 'Produit', 'categorie': 'Catégorie', 'ca': 'CA (DH)', 'volume': 'Volume'}),
                    column_config={
                        "CA (DH)": st.column_config.NumberColumn(format="%.0f DH"),
                        "Volume": st.column_config.NumberColumn(format="%d u")
                    },
                    hide_index=True,
                    use_container_width=True
                )'''
new2 = '''                df_fmt = df_top10.rename(columns={'nom_produit': 'Produit', 'categorie': 'Catégorie', 'ca': 'CA (DH)', 'volume': 'Volume'})
                df_fmt['CA (DH)'] = df_fmt['CA (DH)'].apply(lambda x: f"{x:,.0f} DH".replace(',', ' '))
                df_fmt['Volume'] = df_fmt['Volume'].apply(lambda x: f"{x} u")
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)'''
content = content.replace(old2, new2)

# 3. Page 3
old3 = '''                st.dataframe(
                    df_seg.rename(columns={'segment_client': 'Segment', 'panier_moyen': 'Panier Moyen', 'nb_cmd': 'Nombre Commandes', 'ca_total': 'CA Total (DH)'}),
                    column_config={
                        "Panier Moyen": st.column_config.NumberColumn(format="%.2f DH"),
                        "CA Total (DH)": st.column_config.NumberColumn(format="%.0f DH"),
                        "Nombre Commandes": st.column_config.NumberColumn(format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )'''
new3 = '''                df_fmt = df_seg.rename(columns={'segment_client': 'Segment', 'panier_moyen': 'Panier Moyen', 'nb_cmd': 'Nombre Commandes', 'ca_total': 'CA Total (DH)'})
                df_fmt['Panier Moyen'] = df_fmt['Panier Moyen'].apply(lambda x: f"{x:,.2f} DH".replace(',', ' '))
                df_fmt['CA Total (DH)'] = df_fmt['CA Total (DH)'].apply(lambda x: f"{x:,.0f} DH".replace(',', ' '))
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)'''
content = content.replace(old3, new3)

# 4. Page 4a
old4 = '''                st.dataframe(
                    df_ret.drop(columns=['couleur']).rename(columns={
                        'categorie': 'Catégorie', 
                        'taux_retour': 'Taux Retour (%)', 
                        'nb_retours': 'Retours', 
                        'total_commandes': 'Commandes Totales'
                    }),
                    column_config={
                        "Taux Retour (%)": st.column_config.NumberColumn(format="%.2f%%"),
                        "Retours": st.column_config.NumberColumn(format="%d"),
                        "Commandes Totales": st.column_config.NumberColumn(format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )'''
new4 = '''                df_fmt = df_ret.drop(columns=['couleur']).rename(columns={'categorie': 'Catégorie', 'taux_retour': 'Taux Retour (%)', 'nb_retours': 'Retours', 'total_commandes': 'Commandes Totales'})
                df_fmt['Taux Retour (%)'] = df_fmt['Taux Retour (%)'].apply(lambda x: f"{x:.2f}%")
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)'''
content = content.replace(old4, new4)

# 5. Page 4b
old5 = '''            st.dataframe(
                df_ret_sub.rename(columns={
                    'sous_categorie': 'Sous-Catégorie',
                    'categorie': 'Catégorie',
                    'nb_retours': 'Retours',
                    'total': 'Volume Total',
                    'taux_retour': 'Taux Retour'
                }),
                column_config={
                    "Taux Retour": st.column_config.NumberColumn(format="%.2f%%"),
                    "Retours": st.column_config.NumberColumn(format="%d"),
                    "Volume Total": st.column_config.NumberColumn(format="%d")
                },
                hide_index=True,
                use_container_width=True
            )'''
new5 = '''            df_fmt = df_ret_sub.rename(columns={'sous_categorie': 'Sous-Catégorie', 'categorie': 'Catégorie', 'nb_retours': 'Retours', 'total': 'Volume Total', 'taux_retour': 'Taux Retour'})
            df_fmt['Taux Retour'] = df_fmt['Taux Retour'].apply(lambda x: f"{x:.2f}%")
            st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)'''
content = content.replace(old5, new5)

# 6. Page 6
old6 = '''                st.dataframe(
                    df_liv.rename(columns={
                        'nom_livreur': 'Livreur',
                        'nb_livraisons': 'Livraisons',
                        'delai_moyen_jours': 'Délai Moyen (j)',
                        'nb_livraisons_retard': 'Retards',
                        'taux_retard_pct': 'Retard (%)'
                    }),
                    column_config={
                        "Retard (%)": st.column_config.NumberColumn(format="%.2f%%"),
                        "Délai Moyen (j)": st.column_config.NumberColumn(format="%.2f j"),
                        "Livraisons": st.column_config.NumberColumn(format="%d"),
                        "Retards": st.column_config.NumberColumn(format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )'''
new6 = '''                import pandas as pd
                df_fmt = df_liv.rename(columns={'nom_livreur': 'Livreur', 'nb_livraisons': 'Livraisons', 'delai_moyen_jours': 'Délai Moyen (j)', 'nb_livraisons_retard': 'Retards', 'taux_retard_pct': 'Retard (%)'})
                df_fmt['Retard (%)'] = df_fmt['Retard (%)'].apply(lambda x: f"{x:.2f}%")
                df_fmt['Délai Moyen (j)'] = df_fmt['Délai Moyen (j)'].apply(lambda x: f"{x:.2f} j" if pd.notnull(x) else "N/A")
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)'''
content = content.replace(old6, new6)

with open('mexora_etl/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done replacing.')
