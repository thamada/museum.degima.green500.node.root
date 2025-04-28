From Suresh's blog <http://surumablog.blogspot.com/2008/03/reply-evolution.html>

Suruma font (and the patch) was started off as solution to the issues regarding the shaping of post-base forms of consonants viz. YA,RA,LA & VA , in certain contexts, when they are the rendered in GNU systems (mainly pango).Treating them as ordinary consonants in the shaping engine means they can be used with 'akhand' tag in the font substitution table.ie, the respective form will appear whenever we input  followed by the above mentioned consonant, irrespective of the context.Another issue solved is the post GSUB reordering of the isolated RA sign(used in reformed script),wherein it should be placed in front of the base glyph.This reordering is still to be achieved by any of the rendering mechanisms except the uniscribe.Moreover, using the post base forms for RA and LA leads to weird shaping results when they are followed by NGA, RA, RRA etc. and may more.So this is the raison d'etre for suruma.

Now, with the Rachanas and Meeras which carry the orthographic legacy of 'The Rachana Movement', the 'g01' version was a fork for implementing suruma concepts by removing the uniscribe support.In 'g02', the uniscribe support is retained.The 'g03' is a fine tuned 'g02' where the issues regarding the conjuncts like YRA ,YLA (as in കൊയ്രാള,മൊയ്ലി) etc. are solved.Also the version name is separated from the fonts' internal name.

In '04' version the shaping issues of post-base forms of YA('മുഖ്യമന്ത്രി' പ്രശ്നം) and VA are solved at the font level by adding half form(pre base).The half forms for other consonants are also used for the better shaping of complex syllabic cluster.Many from SMC suggested that the 'g' part be removed because of the uniscribe support is there.Thus the version name.

Now, what about suruma font? In this strange scenario it travelled backward,in a sense, and gets some uniscribe support(not quite).It is now suruma2.

As a demonstrative case for using reformed script with pango, I used Late R K Joshi's GPL'ed font RaghuMalayalam(suggested by Anivar) and made version2 of it based on the principle used in the '04 fonts.

The pango now uses post base forms of YA and VA only.So the support for these fonts are there.The 'കാര്‍ക്കോടകന്‍' issue will be solved once the patches for the same is accepted by the pango people.

See COPYING.txt for details about distributing (with or without modification).
