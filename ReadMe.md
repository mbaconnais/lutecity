# Substitution Assistant Manager

This project was created on the occasion of the [Hays x Manchester City Football City](https://app.hayscodeco.com/events/hackathon/be474355-e892-4604-8db8-0c3019f6c59e) hackathon which took place from 24 March to 24 April 2023.

:3rd_place_medal: 3rd prize of the Hackathon awarded on May 24th 2023 at Manchester.

:womens: **Authors :** Lutecity ([Chloé Gobé](https://github.com/ChloeGobe)
& [Melanie Baconnais](https://github.com/mbaconnais))

:link: **App**  You can find the app [lutecity2023.eu.pythonanywhere.com](http://lutecity2023.eu.pythonanywhere.com/)

<div align="center">
    <img src="img/5569387.jpg" height=200>
    </div>

## Project's description

Deciding to make a substitution or tactical change during a game is not a simple task.
The decision has to be made quickly, with little information, and with possible consequences to the game's dynamics.
We imagine that having a decision support tool that would allow the coaches to rely on analytical elements, combined with their expertise, could help during games.

We want to create a substitution assistant manger with straight-to-the-point and clear information : manager and staff can’t read complex and detailled report during the game

**1. Technical performance**

To reflect the technical performance of the player, several methods can be used. We used the VAEP to track the impact of the player on the probability of increasing or preventing a goal during the game.
Our approach is to study the VAEP value over time, adjusting the value of each action in respect to the type of event (shot, pass, tackle) and the position of the player doing it.
We then display this evolution compared to an individual average evolution obtained by looking at the other games in the dataset

**2. Physical aspect**

Another element for making a change is the physical fatigue of the player.
In the sports science literature, we have identified the concept of a change point in the curves representing metabolism power and have implemented this analysis to indicate to staff the possible need for change.
We have added different metrics that add up to this analysis

## Data used

- Statsbombs OpenData matches, events and lineups for FASWL games
- Manchester City Football provided Statsbomb Data & SecondSpectrum data

## Organisation of the repository

:file_folder: **Data** 

Most of the data used has been removed for a lighter repository

:file_folder: **App**

Code of the Dash application created

:file_folder: **Technical**

- :file_folder:models : Models of ML - VAEP
- Training-VAEP-model.ipynb
- Analyzing-VAEP-games.ipynb
- Player_technical_statistics.ipynb

:file_folder: **Physical**
- Metabolic_power.ipynb
- Player_physical_statistics.ipynb

## References

- Tom Decroos, Lotte Bransen, Jan Van Haaren, and Jesse Davis. _“Actions speak louder than goals: Valuing player actions in soccer.”__ In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, pp. 1851-1861. 2019.
- SoccerAction public notebooks and documentation [here](https://socceraction.readthedocs.io)
- Friends of Tracking, [Lesson on VAEP](https://github.com/soccer-analytics-research/fot-valuing-actions/tree/master/notebooks)
-  _Combining data science and sports science, with Benfica's head of data science. (Part 2)_, Friends of Tracking [video](https://www.youtube.com/watch?v=teCgjQ2ZKNo)

- Image de <a href="https://fr.freepik.com/vecteurs-libre/collection-joueurs-football-design-plat_15291971.htm#query=women%20football&position=8&from_view=search&track=ais">Freepik</a>


