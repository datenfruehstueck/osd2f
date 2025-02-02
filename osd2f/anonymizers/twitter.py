import typing
import re
from .genuine import unravel_hierarchical_fields

twitter_list_usernames = ['@__nachrichten__',
                          '@_HORIZONT',
                          '@_rontaler',
                          '@_Wochenblatt',
                          '@1LIVE',
                          '@20min',
                          '@3sat',
                          '@aachenerzeitung',
                          '@Aarauer_Nachr',
                          '@AargauerZeitung',
                          '@abendblatt',
                          '@Abendzeitung',
                          '@achgut_com',
                          '@actufr',
                          '@adpunktum',
                          '@aktuellobwalden',
                          '@Allgaeu',
                          '@Alpenschau',
                          '@an_topnews',
                          '@annabelle_mag',
                          '@ANZEIGER_NEWS',
                          '@AnzeigerDRegion',
                          '@AOL',
                          '@ARD_Presse',
                          '@ARDmediathek',
                          '@ardmoma',
                          '@ARDText',
                          '@ARTEde',
                          '@asr_blog',
                          '@ATV',
                          '@AugustinZeitung',
                          '@awp_de',
                          '@AZ_Allgaeu',
                          '@AZ_Augsburg',
                          '@aznachrichten',
                          '@AZUelzen',
                          '@bachheimercom',
                          '@badischezeitung',
                          '@baernerbaer',
                          '@Bauernzeitung_D',
                          '@BauernZeitung1',
                          '@bayern1',
                          '@bayern2',
                          '@bayern3',
                          '@bazonline',
                          '@BBV_Bocholt',
                          '@BeobachterRat',
                          '@BERLINER_KURIER',
                          '@BernerZeitung',
                          '@bgland24',
                          '@bgzonline',
                          '@BIDeutschland',
                          '@bielertagblatt',
                          '@BILANZ',
                          '@BILD',
                          '@BILD_Sport',
                          '@BILDblog',
                          '@BJBerlinJournal',
                          '@bkz_online',
                          '@Blickch',
                          '@bluenews_de',
                          '@BNN_BaNeuNa',
                          '@boehme_zeitung',
                          '@boersenzeitung',
                          '@BorkenerZeitung',
                          '@bote_online',
                          '@BoyensMedien',
                          '@BR_Franken',
                          '@BR_KLASSIK',
                          '@BR_Presse',
                          '@BR24',
                          '@bremeneins',
                          '@BremenVier',
                          '@BremenZwei',
                          '@BS_Zeitung',
                          '@BSAktuell',
                          '@BTBaden',
                          '@BUNTE',
                          '@bvz_online',
                          '@bzBasel',
                          '@bzberlin',
                          '@campact',
                          '@cashch',
                          '@cashkurs',
                          '@cezett',
                          '@CH_Wochenende',
                          '@chiemgau24',
                          '@CHIP_online',
                          '@cicero_online',
                          '@comeon_de',
                          '@COMPACTMagazin',
                          '@COMPUTERBILD',
                          '@COMPUTERWOCHE',
                          '@computerworldch',
                          '@coop_ch',
                          '@CorreodeEspana',
                          '@CorriereCitta',
                          '@COSMO__ARD',
                          '@CriminImmigratl',
                          '@DASDING',
                          '@DasErste',
                          '@DasSauerland',
                          '@DATUMSDZ',
                          '@dcexaminer',
                          '@DECointelegraph',
                          '@der_Grazer',
                          '@Der_Postillon',
                          '@Der_Teckbote',
                          '@derbund',
                          '@derfreitag',
                          '@DerLandanzeiger',
                          '@derspiegel',
                          '@derStandardat',
                          '@DeutscheWelle',
                          '@Dewezet',
                          '@DiarioSUR',
                          '@Die_Harke',
                          '@diefurche',
                          '@DieGlocke',
                          '@DieMonatliche',
                          '@DiePressecom',
                          '@DieTagespost',
                          '@DieTagesstimme',
                          '@DIEZEIT',
                          '@DieZrcherin',
                          '@DigitalSevilla',
                          '@DirektnoHR',
                          '@dk_DEL',
                          '@DLF',
                          '@dlfkultur',
                          '@dlfnova',
                          '@dmontanes',
                          '@dnn_online',
                          '@donaukurier',
                          '@Donuncutschweiz',
                          '@dorfheftli',
                          '@dossier_',
                          '@DWN_de',
                          '@dwnews',
                          '@DZ_Duelmen',
                          '@ebsscharflinks',
                          '@ecd_',
                          '@Echo_Online',
                          '@echo24_de',
                          '@EconomiaED_',
                          '@efonline',
                          '@ein_prozent',
                          '@eingeschenkt_TV',
                          '@einmorgenpost',
                          '@EinsiedlerANZ',
                          '@ejournalschweiz',
                          '@ejzgezwitscher',
                          '@El_Plural',
                          '@elboletinmadrid',
                          '@elcomerciodigit',
                          '@elconfidencial',
                          '@elcorreo_com',
                          '@elcorreogallego',
                          '@elCorreoWeb',
                          '@eldiarioes',
                          '@eldiatenerife',
                          '@eldigitalCLM',
                          '@eleconomista',
                          '@elespanolcom',
                          '@elmundoes',
                          '@ElNacionalWeb',
                          '@elperiodico',
                          '@elpuntavui',
                          '@ELTIEMPO',
                          '@EmderZeitung',
                          '@engadinerpost',
                          '@ensonhaber',
                          '@EntlebucherAnz',
                          '@EPExtremadura',
                          '@EpochTimes',
                          '@erstaunlich_at',
                          '@ESdiario_com',
                          '@estrelladigital',
                          '@euronews',
                          '@europapress',
                          '@Europe1',
                          '@exopolitik',
                          '@expansioncom',
                          '@express24',
                          '@ExpressandStar',
                          '@extratippcom',
                          '@extremnews',
                          '@ez_online',
                          '@F_Desouche',
                          '@Faktum_Magazin',
                          '@falter_at',
                          '@fanpage',
                          '@fattoquotidiano',
                          '@FAZ_NET',
                          '@faznet',
                          '@FCN2go',
                          '@FeminaCh',
                          '@FinancialTimes',
                          '@finanzenCH',
                          '@FinanzenNet',
                          '@finews_ch',
                          '@fischundfleisch',
                          '@FiveThirtyEight',
                          '@Flensborg_Avis',
                          '@fm1today',
                          '@FN_Aktien',
                          '@fnp_zeitung',
                          '@focusonline',
                          '@Forbes_DA_',
                          '@FortuneMagazine',
                          '@fox13',
                          '@FOX13News',
                          '@FOX2now',
                          '@fox4kc',
                          '@FOX59',
                          '@fox6now',
                          '@fox8news',
                          '@FOX9',
                          '@FoxBusiness',
                          '@FOXLA',
                          '@FoxNews',
                          '@FOXTV',
                          '@fr',
                          '@france_soir',
                          '@FRANCE24',
                          '@France3tv',
                          '@francebleu',
                          '@franceculture',
                          '@franceinfo',
                          '@franceinter',
                          '@Francetele',
                          '@francetv',
                          '@Frankenpost',
                          '@freie_presse',
                          '@freierschweizer',
                          '@freiesicht_org',
                          '@freieswort',
                          '@FreieWeltEu',
                          '@FreieWeltNet',
                          '@FreitumBlog',
                          '@Friburgera',
                          '@fricktalinfo',
                          '@Fritz_offiziell',
                          '@FrNachrichten',
                          '@FTageblatt',
                          '@fuldaerzeitung',
                          '@futurezoneat',
                          '@FuW_News',
                          '@ga_online',
                          '@gabonn',
                          '@gaceta_es',
                          '@Gaeubote',
                          '@gala',
                          '@GALAmagazine',
                          '@GanzeWOCHE',
                          '@gasteizhoy',
                          '@GazzettaDelSud',
                          '@gazzettaparma',
                          '@Gazzettino',
                          '@GdB_it',
                          '@geaonline',
                          '@GeoliticoNews',
                          '@GermanForeignPo',
                          '@GEWINNcom',
                          '@GHI_GE',
                          '@Giornalone',
                          '@gkreisblatt',
                          '@Glasgow_Times',
                          '@GlucksPost',
                          '@GMA',
                          '@GMX',
                          '@GN_Nordhorn',
                          '@gnzonline',
                          '@goetageblatt',
                          '@golem',
                          '@googlenews',
                          '@goslarsche',
                          '@granadahoy',
                          '@graswurzelrevo1',
                          '@Grigione_Italia',
                          '@gruyere_journal',
                          '@GT_Gmuend',
                          '@HA1725',
                          '@Haberler',
                          '@HalloMunchen',
                          '@hallowil_news',
                          '@handelsblatt',
                          '@Handelszeitung',
                          '@Harlinger1862',
                          '@HarzKurier',
                          '@heidelberg_24',
                          '@heimatzeitungen',
                          '@heiseonline',
                          '@HellwegerNews',
                          '@heraldoes',
                          '@hessenschau',
                          '@Heute_at',
                          '@hinews',
                          '@Hintergrund_de',
                          '@HLN',
                          '@HNA_online',
                          '@HoefnerVolks',
                          '@HonggerQ',
                          '@hoyextremadura',
                          '@hr1',
                          '@hr3',
                          '@ht_nachrichten',
                          '@huelva_info',
                          '@HuffPost',
                          '@hulllive',
                          '@humanite_fr',
                          '@HZOnline',
                          '@ideal_granada',
                          '@idowa',
                          '@ilfoglio_it',
                          '@ilgiornale',
                          '@ilmanifesto',
                          '@ilmessaggeroit',
                          '@IlPrimatoN',
                          '@Independent',
                          '@infosperber',
                          '@inFranken',
                          '@innsalzach24',
                          '@inside_it',
                          '@ivz_aktuell',
                          '@journal21',
                          '@Junge_Freiheit',
                          '@jungewelt',
                          '@JungfrauZeitung',
                          '@kabeleins',
                          '@KAgezwitscher',
                          '@kanal9wallis',
                          '@kanews',
                          '@kathch',
                          '@KircheBunt',
                          '@kleinezeitung',
                          '@kn_online',
                          '@KoelnischeR',
                          '@konkretmagazin',
                          '@Kontrast_at',
                          '@kraftzeitung',
                          '@krautreporter',
                          '@Kreisblatt',
                          '@KreisblattHalle',
                          '@Kreiszeitung',
                          '@kreiszeitungbb',
                          '@KreiszeitungWB',
                          '@krone_at',
                          '@KSTA',
                          '@Kulturzeitung80',
                          '@kurier_online',
                          '@KURIERat',
                          '@la_tele',
                          '@LaCoteJournal',
                          '@laliberte',
                          '@landbote',
                          '@LAOLA1_at',
                          '@LAredaktion',
                          '@laregione',
                          '@lecourrier',
                          '@lejds',
                          '@lemanbleutv',
                          '@Lematinch',
                          '@lemondefr',
                          '@lenouvelliste',
                          '@lestrepublicain',
                          '@LeTemps',
                          '@Lillustre',
                          '@links_netz',
                          '@linksnetde',
                          '@linth_zeitung',
                          '@LiZLimmattaler',
                          '@LKZ_Leonberg',
                          '@LKZ_online',
                          '@LN_Online',
                          '@lr_online',
                          '@LuzernerZeitung',
                          '@LuzeRund',
                          '@LVZ',
                          '@lzgezwitscher',
                          '@lzonline',
                          '@magazin_daslamm',
                          '@mainecho_de',
                          '@mainpost',
                          '@manager_magazin',
                          '@maz_online',
                          '@MDR_SAN',
                          '@MDR_SN',
                          '@mdr_th',
                          '@MDRAktuell',
                          '@mdrde',
                          '@mdrjump',
                          '@mdrkultur',
                          '@MDRSPUTNIK',
                          '@MediasetTgcom24',
                          '@MedienhausBauer',
                          '@Medienwoche',
                          '@MedInfinityIT',
                          '@MEGAPHONmagazin',
                          '@meinbezirk_at',
                          '@menschenzeitung',
                          '@merkur_de',
                          '@mittelbadische',
                          '@mittelhessende',
                          '@MMnews1',
                          '@Monsantogohome',
                          '@mopo',
                          '@morgenpost',
                          '@mosaik_blog',
                          '@mozde',
                          '@msnde',
                          '@MT_Online',
                          '@MVRheine',
                          '@MVTV20',
                          '@MYTF1',
                          '@mz_de',
                          '@MZ_MUENSTER',
                          '@MZ_Online',
                          '@mzwebde',
                          '@na_presseportal',
                          '@NachDenkSeiten',
                          '@nachrichten_at',
                          '@nau_live',
                          '@ndaktuell',
                          '@ndr',
                          '@ndr2',
                          '@NDRinfo',
                          '@ndrkultur',
                          '@ndrmv',
                          '@NDRnds',
                          '@NDRsh',
                          '@ndtv',
                          '@NeckarChronik',
                          '@neopresse',
                          '@netzfrauen',
                          '@neuepresse',
                          '@NEUEVT',
                          '@NEWS',
                          '@news_de',
                          '@news_mondo_h24',
                          '@News12',
                          '@news38_de',
                          '@News64News',
                          '@newscomauHQ',
                          '@Newsday',
                          '@Newser',
                          '@NewsRepublic',
                          '@Newsweek',
                          '@NewYorker',
                          '@neXtquotidiano',
                          '@NEZ_Online',
                          '@NJOYDE',
                          '@NN_Online',
                          '@NNNonline',
                          '@noen_online',
                          '@nordbayern',
                          '@Nordkurier',
                          '@nordseezeitung',
                          '@nortecastilla',
                          '@NovoArgumente',
                          '@novostionline',
                          '@noz_de',
                          '@NPCoburg',
                          '@NPR',
                          '@NQVS',
                          '@NRZMeinung',
                          '@ntvde',
                          '@nwnews',
                          '@nwzonline',
                          '@nytimes',
                          '@NZ_Online',
                          '@NZZ',
                          '@NZZaS',
                          '@oberhessische',
                          '@ObermainTB',
                          '@oe24at',
                          '@oe24tv',
                          '@OMonlineDe',
                          '@on_online_de',
                          '@ON_Redaktion',
                          '@onetz_de',
                          '@online_MM',
                          '@opmarburg',
                          '@ORF',
                          '@osthessennewsde',
                          '@OstschweizamSon',
                          '@OTZonline',
                          '@OW_Zeitung',
                          '@oz_online_de',
                          '@OZlive',
                          '@P_I',
                          '@pazpeine',
                          '@PBS',
                          '@PCtipp',
                          '@PDmedien',
                          '@persoenlichcom',
                          '@PflzischerMerku',
                          '@phoenix_de',
                          '@PME_NEWS',
                          '@PMEmagazine_',
                          '@PNN_de',
                          '@pnp',
                          '@Pocket',
                          '@POLIZEI_SCHWEIZ',
                          '@Pressecop24com',
                          '@Pressehaus',
                          '@prime_news_ch',
                          '@profilonline',
                          '@promiflash',
                          '@PROPAGANDAFRONT',
                          '@propagandaschau',
                          '@ProSieben',
                          '@puls24news',
                          '@PZ_Nachrichten',
                          '@pz_online',
                          '@pznews',
                          '@qpress42',
                          '@quotenqueen',
                          '@radioeins',
                          '@RadioHochstift',
                          '@RadioMKofficial',
                          '@radiorfj',
                          '@radiorjb',
                          '@radiorottu',
                          '@RadioTeleSuisse',
                          '@RadioUtopie_de',
                          '@RalphGoerlich',
                          '@Ramin_Peymani',
                          '@rbb88acht',
                          '@rbbKultur',
                          '@realnewspunch',
                          '@RedRegionews',
                          '@remszeitung',
                          '@ReportagenCH',
                          '@RepublikMagazin',
                          '@Reussbote',
                          '@Reuters',
                          '@reuters_de',
                          '@rheinpfalz',
                          '@rheintal24',
                          '@Rheintalonline',
                          '@RheinZeitung',
                          '@RN_DORTMUND',
                          '@rnfde_feed',
                          '@RNZonline',
                          '@rosenheim24',
                          '@rotefahnenews',
                          '@rponline',
                          '@RSInews',
                          '@RT_com',
                          '@rt_deutsch',
                          '@RTL_com',
                          '@rtl_direkt',
                          '@rtl2',
                          '@RTLplus',
                          '@RTLWEST',
                          '@RTRSRG',
                          '@RUHR24news',
                          '@RZ_Rheiderland',
                          '@saechsischeDE',
                          '@saez_bms',
                          '@Salzburg24',
                          '@sarganserlander',
                          '@sat1',
                          '@Schaffhauser_AZ',
                          '@Schwaebische',
                          '@SchwaePo',
                          '@schwarzwaelder',
                          '@SchweizerBauer',
                          '@schweizerillu',
                          '@schweizerzeit',
                          '@SeetalerBote',
                          '@SempacherWoche',
                          '@SGTageblatt',
                          '@shlandzeitung',
                          '@SHN_News',
                          '@shz_de',
                          '@SiegenerZeitung',
                          '@SiNetz',
                          '@SkyDeutschland',
                          '@SkySportDE',
                          '@Slate',
                          '@Slatefr',
                          '@sn_aktuell',
                          '@sn_online',
                          '@soesteranzeiger',
                          '@sonntagsblatt',
                          '@sonntagszeitung',
                          '@spektrum',
                          '@SPIEGELTV',
                          '@splinter_news',
                          '@SPORT1',
                          '@SPORT1eSports',
                          '@SPORTBILD',
                          '@sportch',
                          '@Sportde',
                          '@sportschau',
                          '@SputnikInt',
                          '@SRF',
                          '@srfnews',
                          '@staatsversagen',
                          '@Staatszeitung',
                          '@StadtAnzeigerO',
                          '@STagblatt',
                          '@standardnews',
                          '@StarTribune',
                          '@sternde',
                          '@stimmeonline',
                          '@StN_News',
                          '@StrettoWeb',
                          '@StZ_NEWS',
                          '@sudinfo_be',
                          '@sudouest',
                          '@Suedkurier_News',
                          '@suedostschweiz',
                          '@SunSentinel',
                          '@Suntimes',
                          '@SurseerWoche',
                          '@svz_de',
                          '@swissinfo_de',
                          '@SWPde',
                          '@SWR2',
                          '@swr3',
                          '@SWRAktuellBW',
                          '@SWRAktuellRP',
                          '@SWRpresse',
                          '@SZ',
                          '@SZ_Bayern',
                          '@SZ_Dachau',
                          '@SZ_Ebersberg',
                          '@SZ_Freising',
                          '@SZ_Muenchen',
                          '@SZ_Politik',
                          '@SZ_Sport',
                          '@SZ_TopNews',
                          '@SZ_Wirtschaft',
                          '@szaktuell',
                          '@SZLZ1',
                          '@szmagazin',
                          '@SZSolothurn',
                          '@t3n',
                          '@TAG24',
                          '@Tag24B',
                          '@TAG24BI',
                          '@TAG24CH',
                          '@TAG24DD',
                          '@TAG24EF',
                          '@TAG24ERZ',
                          '@TAG24FFM',
                          '@TAG24G',
                          '@TAG24HH',
                          '@Tag24J',
                          '@TAG24Koeln',
                          '@TAG24LE',
                          '@TAG24M',
                          '@TAG24MI',
                          '@TAG24PB',
                          '@Tag24S',
                          '@Tag24V',
                          '@Tag24Z',
                          '@Tagblatt',
                          '@tagblatt_ch',
                          '@TagblattOnline',
                          '@TagblattZuerich',
                          '@tageblatt_lu',
                          '@Tageblatt_News',
                          '@Tageblatt_Pi',
                          '@TAGEBLATTonline',
                          '@tagesanzeiger',
                          '@tagesschau',
                          '@Tagesspiegel',
                          '@tagi_magi',
                          '@TAH_Lokal',
                          '@TAOnline',
                          '@tazgezwitscher',
                          '@TechCrunch',
                          '@Tele1ZF',
                          '@Telebasel',
                          '@telebielinguetv',
                          '@telecincoes',
                          '@Telegrafisti',
                          '@telegrafrs',
                          '@Telegraph',
                          '@telegraphga',
                          '@Telemundo',
                          '@telepolis_news',
                          '@teleticino',
                          '@TeleZueri',
                          '@Tempi_it',
                          '@TermometroPol',
                          '@TessinerZeitung',
                          '@TheEconomist',
                          '@theeuropean',
                          '@TheOklahoman_',
                          '@TichysEinblick',
                          '@tipszeitung',
                          '@TLZnews',
                          '@Trentin0',
                          '@TTNachrichten',
                          '@TV5MONDE',
                          '@tvo_online',
                          '@tzmuenchen',
                          '@udinetoday',
                          '@uebermedien',
                          '@UKTVPlay',
                          '@Unbestechlichen',
                          '@UnsereZeit_UZ',
                          '@UnsereZeitung',
                          '@unterkaerntner',
                          '@unzensuriert',
                          '@UOL',
                          '@UrnerZeitung',
                          '@USATODAY',
                          '@usatodaysports',
                          '@usnews',
                          '@valenciaplaza',
                          '@Valeurs',
                          '@vaterlandnews',
                          '@VestiOnLine',
                          '@VICE',
                          '@vice_de',
                          '@viennaonline',
                          '@VilaWeb',
                          '@VNRedaktion',
                          '@VOANews',
                          '@Vogtland_News',
                          '@Volksblatt',
                          '@Volksfreund',
                          '@Volksstimme',
                          '@Volksstimme_CH',
                          '@Volksverpetzer',
                          '@Vorarlberg',
                          '@VotumEins',
                          '@VOXde',
                          '@voxdotcom',
                          '@voz_populi',
                          '@VRMwirbewegen',
                          '@WA_online',
                          '@WakeNewsRadio',
                          '@WAnzeiger',
                          '@washingtonpost',
                          '@WashTimes',
                          '@watson_de',
                          '@watson_news',
                          '@WAZ_Bochum',
                          '@WAZ_Essen',
                          '@WAZ_Redaktion',
                          '@wazwolfsburg',
                          '@WDR',
                          '@WDR2',
                          '@wdr5',
                          '@WDRaktuell',
                          '@WEAU13News',
                          '@webecodibergamo',
                          '@welt',
                          '@weltnetzTV',
                          '@Weltwoche',
                          '@Werra_Rundschau',
                          '@weserkurier',
                          '@westfalenblatt',
                          '@WestfalischerA',
                          '@WestJournalism',
                          '@WEWS',
                          '@WienerZeitung',
                          '@WilerZeitung',
                          '@WillisauerBote',
                          '@Winti_WiZe',
                          '@WIRED',
                          '@wireditalia',
                          '@wiwo',
                          '@wjxt4',
                          '@wknachrichten',
                          '@wlz_online',
                          '@WN_Redaktion',
                          '@WN_Wolfsburg',
                          '@wn24aktuell',
                          '@wnoz',
                          '@Wochen_Zeitung',
                          '@Wochenblatt1791',
                          '@Wochenzeitung',
                          '@WPXI',
                          '@WrldJusticeNews',
                          '@wsbtv',
                          '@WSJ',
                          '@Wuemme_Zeitung',
                          '@wxyzdetroit',
                          '@wz_net',
                          '@WZ_Wetterau',
                          '@wznewsline',
                          '@WZonline',
                          '@YahooNews',
                          '@yoicenet',
                          '@YOUFM',
                          '@ZAK_Redaktion',
                          '@ZaroPresse',
                          '@ZDF',
                          '@zeitonline',
                          '@ZeitungExpress',
                          '@zentralplus',
                          '@ZevenerZeitung',
                          '@ZSZonline',
                          '@zt_info',
                          '@zueriost',
                          '@zueritoday',
                          '@zuerst_magazin',
                          '@ZUnterland',
                          '@zvw_redaktion',
                          '@Zwitschern_UA',
                          '@zwoelf_app',
                          '@Berliner Zeitung',
                          '@Bietigheimer Zeitung',
                          '@dpa',
                          '@Freie Presse',
                          '@Hannoversche Allgemeine Zeitung / HAZ',
                          '@journaldemorges',
                          '@jouwatch',
                          '@lahrerzeitung',
                          '@mittelhessen.de',
                          '@Westfalen-Blatt']


def twitter_anonymize_generic_re_callback(match):
    if match.group(0) not in twitter_list_usernames:
        return "@<user>"
    else:
        return match.group(0)


def twitter_anonymize_generic(field: str) -> str:
    return re.sub('@[a-zA-Z0-9_]+', twitter_anonymize_generic_re_callback, field)


async def twitter_anonymize_handles(entry: typing.Dict[str, typing.Any], text_field: str = '') \
        -> typing.Dict[str, typing.Any]:
    if text_field in entry:
        entry[text_field] = twitter_anonymize_generic(entry[text_field])
    elif text_field.__contains__('.'):
        entry = await unravel_hierarchical_fields(entry, text_field, twitter_anonymize_handles)
    return entry


async def twitter_anonymize_usernames(entry: typing.Dict[str, typing.Any], username_field: str = '') \
        -> typing.Dict[str, typing.Any]:
    if username_field in entry:
        if '@' + entry[username_field] not in twitter_list_usernames:
            entry[username_field] = '<user>'
    elif username_field.__contains__('.'):
        entry = await unravel_hierarchical_fields(entry, username_field, twitter_anonymize_usernames)
    return entry
