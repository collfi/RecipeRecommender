This is just project.

git status
git add ....
git rm ....
git commit
git push origin master
git pull // zobranie zo serveru
git pull origin master

todo:
collfi do nedele:
-- 1. prestuduj si zmeny co som spravil
-- 2. dorobit show_entry, pokial je oretingovany dany recept userom tak to zobrazit aj v hviezdickach, inspirovat sa favoritom
   toto zistis lahko z mongo User
-- 3. upravit tagy takto https://github.com/xoxco/jQuery-Tags-Input   bude to omnoho cool, budes sa musiet pohrat asi s javascriptom/jquery/ajaxom mas to ukazane v show_entry.html
-- 4. vytvor dalsich dvoch uzivatelov a tri recepty v database.py a recommender.py
-- 5. prestuduj si co to je cron.txt a spust $crontab cron.txt // ten cron.txt si budes musiet upravit ale nepridavaj git add cron.txt prosim nech to nerozbijes mne :)
   http://code.tutsplus.com/tutorials/scheduling-tasks-with-cron-jobs--net-8800
-- v engine.py si uprav sys.path, sprav funkciu mostfavorite v engine.py ktora zisti top 5 najviac favorites receptov a ulozi ich do monga, uz som ti vytvoril model
   NonPersonal kde pojdu id tych top receptov a model Recipe kde sa nachadzaju favorites  s ktorymi budes pocitat,
   vo vysledku to bude vypadat tak ze ten engine.py sa bude pustat cronom kazdych x minut a spocita top5favorites

cospel dalsi tyzden:
-- 1. zobrazenie top5favorites
-- 2. upravenie dizajnu pre recept, zobrazenie priemerneho hodnotenia pre recept, pocitanie priemernych hodnoteni s cronom
-- 3. zacanie prace na content based recommendation
