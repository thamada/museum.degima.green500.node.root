# Copyright 2007  Red Hat, Inc.
#
# Lingning Zhang <lizhang@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

languages_Dict = { "af_ZA":"afrikaans-support", \
             "sq_AL.UTF-8":"albanian-support", \
             "ar_DZ.UTF-8":"arabic-support", \
             "ar_BH.UTF-8":"arabic-support", \
             "ar_EG.UTF-8":"arabic-support", \
             "ar_IN.UTF-8":"arabic-support", \
             "ar_IQ.UTF-8":"arabic-support", \
             "ar_JO.UTF-8":"arabic-support", \
             "ar_KW.UTF-8":"arabic-support", \
             "ar_LB.UTF-8":"arabic-support", \
             "ar_LY.UTF-8":"arabic-support", \
             "ar_MA.UTF-8":"arabic-support", \
             "ar_OM.UTF-8":"arabic-support", \
             "ar_QA.UTF-8":"arabic-support", \
             "ar_SA.UTF-8":"arabic-support", \
             "ar_SD.UTF-8":"arabic-support", \
             "ar_SY.UTF-8":"arabic-support", \
             "ar_TN.UTF-8":"arabic-support", \
             "ar_AE.UTF-8":"arabic-support", \
             "ar_YE.UTF-8":"arabic-support", \
             "as_IN.UTF-8":"assamese-support", \
             "ast_ES.UTF-8":"asturian-support", \
             "eu_ES.UTF-8":"basque-support", \
             "be_BY.UTF-8":"belarusian-support", \
             "bn_BD.UTF-8":"bengali-support", \
             "bn_IN.UTF-8":"bengali-support", \
             "bs_BA":"bosnian-support", \
             "br_FR":"breton-support", \
             "bg_BG.UTF-8":"bulgarian-support", \
             "ca_ES.UTF-8":"catalan-support", \
             "zh_HK.UTF-8":"chinese-support", \
             "zh_CN.UTF-8":"chinese-support", \
             "zh_TW.UTF-8":"chinese-support", \
             "kw_GB.UTF-8":"none", \
             "hr_HR.UTF-8":"croatian-support", \
             "cs_CZ.UTF-8":"czech-support", \
             "da_DK.UTF-8":"danish-support", \
             "nl_BE.UTF-8":"dutch-support", \
             "nl_NL.UTF-8":"dutch-support", \
             "en_AU.UTF-8":"none", \
             "en_BW.UTF-8":"none", \
             "en_CA.UTF-8":"none", \
             "en_DK.UTF-8":"none", \
             "en_GB.UTF-8":"british-support", \
             "en_HK.UTF-8":"none", \
             "en_IN.UTF-8":"none", \
             "en_IE.UTF-8":"none", \
             "en_NZ.UTF-8":"none", \
             "en_PH.UTF-8":"none", \
             "en_SG.UTF-8":"none", \
             "en_ZA.UTF-8":"none", \
             "en_US.UTF-8":"none", \
             "en_ZW.UTF-8":"none", \
             "et_EE.UTF-8":"estonian-support", \
             "fo_FO.UTF-8":"faroese-support", \
             "fi_FI.UTF-8":"finnish-support", \
             "fr_BE.UTF-8":"french-support", \
             "fr_CA.UTF-8":"french-support", \
             "fr_FR.UTF-8":"french-support", \
             "fr_LU.UTF-8":"french-support", \
             "fr_CH.UTF-8":"french-support", \
             "gl_ES.UTF-8":"galician-support", \
             "de_AT.UTF-8":"german-support", \
             "de_BE.UTF-8":"german-support", \
             "de_DE.UTF-8":"german-support", \
             "de_LU.UTF-8":"german-support", \
             "de_CH.UTF-8":"german-support", \
             "el_GR.UTF-8":"greek-support", \
             "kl_GL.UTF-8":"none", \
             "gu_IN.UTF-8":"gujarati-support", \
             "he_IL.UTF-8":"hebrew-support", \
             "hi_IN.UTF-8":"hindi-support", \
             "hu_HU.UTF-8":"hungarian-support", \
             "is_IS.UTF-8":"icelandic-support", \
             "id_ID.UTF-8":"indonesian-support", \
             "ga_IE.UTF-8":"irish-support", \
             "it_IT.UTF-8":"italian-support", \
             "it_CH.UTF-8":"italian-support", \
             "ja_JP.UTF-8":"japanese-support", \
             "kn_IN.UTF-8":"kannada-support", \
             "ko_KR.UTF-8":"korean-support", \
             "lo_LA.UTF-8":"lao-support", \
             "lv_LV.UTF-8":"latvian-support", \
             "lt_LT.UTF-8":"lithuanian-support", \
             "mk_MK.UTF-8":"none", \
             "ml_IN.UTF-8":"malayalam-support", \
             "ms_MY.UTF-8":"malay-support", \
             "mt_MT.UTF-8":"none", \
             "gv_GB.UTF-8":"gaelic-support", \
             "mr_IN.UTF-8":"marathi-support", \
             "se_NO":"none", \
             "ne_NP.UTF-8":"nepali-support", \
             "nb_NO.UTF-8":"norwegian-support", \
             "nn_NO.UTF-8":"norwegian-support", \
             "oc_FR":"none", \
             "or_IN.UTF-8":"oriya-support", \
             "fa_IR.UTF-8":"persian-support", \
             "pl_PL.UTF-8":"polish-support", \
             "pt_BR.UTF-8":"portuguese-support", \
             "pt_PT.UTF-8":"portuguese-support", \
             "pa_IN.UTF-8":"punjabi-support", \
             "ro_RO.UTF-8":"romanian-support", \
             "ru_RU.UTF-8":"russian-support", \
             "ru_UA.UTF-8":"russian-support", \
             "sr_RS.UTF-8":"serbian-support", \
             "sr_RS.UTF-8@latin":"serbian-support", \
             "si_LK.UTF-8":"sinhala-support", \
             "sk_SK.UTF-8":"slovak-support", \
             "sl_SI.UTF-8":"slovenian-support", \
             "es_AR.UTF-8":"spanish-support", \
             "es_BO.UTF-8":"spanish-support", \
             "es_CL.UTF-8":"spanish-support", \
             "es_CO.UTF-8":"spanish-support", \
             "es_CR.UTF-8":"spanish-support", \
             "es_DO.UTF-8":"spanish-support", \
             "es_SV.UTF-8":"spanish-support", \
             "es_EC.UTF-8":"spanish-support", \
             "es_GT.UTF-8":"spanish-support", \
             "es_HN.UTF-8":"spanish-support", \
             "es_MX.UTF-8":"spanish-support", \
             "es_NI.UTF-8":"spanish-support", \
             "es_PA.UTF-8":"spanish-support", \
             "es_PY.UTF-8":"spanish-support", \
             "es_PE.UTF-8":"spanish-support", \
             "es_PR.UTF-8":"spanish-support", \
             "es_ES.UTF-8":"spanish-support", \
             "es_US.UTF-8":"spanish-support", \
             "es_UY.UTF-8":"spanish-support", \
             "es_VE.UTF-8":"spanish-support", \
             "sv_FI.UTF-8":"swedish-support", \
             "sv_SE.UTF-8":"swedish-support", \
             "tl_PH":"tagalog-support", \
             "ta_IN.UTF-8":"tamil-support", \
             "te_IN.UTF-8":"telugu-support", \
             "th_TH.UTF-8":"thai-support", \
             "tr_TR.UTF-8":"turkish-support", \
             "uk_UA.UTF-8":"ukrainian-support", \
             "ur_PK":"urdu-support", \
             "uz_UZ":"none", \
             "wa_BE@euro":"none", \
             "cy_GB.UTF-8":"welsh-support", \
             "xh_ZA.UTF-8":"xhosa-support", \
             "zu_ZA.UTF-8":"zulu-support",\
	     "mai_IN.UTF-8":"maithili-support",\
	     "sd_IN.UTF-8":"sindhi-support",\
	     "ks_IN.UTF-8":"kashmiri-support",\
	     "sd_IN@devanagari.UTF-8":"sindhi-support",\
	     "ks_IN@devanagari.UTF-8":"kashmiri-support" }

def get_groupID_from_language(language):
	return languages_Dict[language]


		
