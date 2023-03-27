# analogy-gluten-free
Evaluates gluten-free word embeddings of Hungarian in the word analogy task

What are gluten-free word embeddings?
The idea of langue modeling with sub-word level units is not new either 
universally (for a summary, see [Nemeskey 2017](https://hlt.bme.hu/en/publ/emLam)) or 
in Hungarian NLP (from phrase-based statistical machine translation to static word embeddings (Siklósi and Novák [2016 in Hungarian](http://acta.bibl.u-szeged.hu/58957/), Siklósi [2016](https://link.springer.com/chapter/10.1007/978-3-319-75477-2_7)).
The pun _gluten-free_ comes from the term agglutinative for languages that glue suffixes to word stems to mark grammatical features.

```
jelmondatával → jelmondat <poss> <cas<ins>>
akartak → akar <past> <plur>
```
Example by Nemeskey (2017).

This modest project evaluates gluten-free word embeddings in the Hungarian equivalent of the word analogy task (Mikolov+ 2013) 
for the purposes of the [PhD thesis](https://hlt.bme.hu/hu/publ/makrai-thesis) of Márton Makrai.
The thesis introduces the task in Section 4.2.7., and the results of this project are reported in Section 7.4.
