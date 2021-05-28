# Scraping licencí ERÚ na výrobu elektřiny

Získání [informací o držitelích](https://www.eru.cz/cs/licence/informace-o-drzitelich) a scraping údajů z udělených [licencí](http://licence.eru.cz/) z webů Energetického regulačního úřadu.

Pomocí balíčku `holders` lze získat informace z xml souborů vždy pro určitý předmět licence (výroba elektřiny, distribuce plynu), které obsahují číslo licence (původně `cislo_licence`, zde `id`).

Podle čísel licencí je potom možné díky balíčku `licenses` scrapovat data pro příslušnou licenci (zatím pouze pro výrobu elektřiny a výrobu tepelné energie).

Pouze získání aktuálních dat v daný čas do csv souborů.
