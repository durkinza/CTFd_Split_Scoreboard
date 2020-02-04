# CTFd Split Scoreboard

Splits the scoreboard by the selected attribute.


## Dependencies

This plugin requires the [CTFd_Team_Attributes plugin](https://github.com/durkinza/CTFd_Team_Attributes).


## Admin Interface

![Admins split scoreboard interfcae](imgs/Admin-page.png)

Admins can pick which attribute of the teams they wish to split the scoreboard on. Currently this plugin only supports splitting the scorebaord on attributes set by the [CTFd_Team_Attributes plugin](https://github.com/durkinza/CTFd_Team_Attributes), but will soon support splitting the score board by team size, location, and affiliation. 
Admins can decide if they wish to offer the custom scoreboard tab. This tab will allow users to select the teams they want to see ranked against eachother. This is useful for groups who wish to see how they rank against their peers, such as student teams all competing in the same class room. 

![Options available](imgs/Options.png)





## Scoreboard Interface

The scoreboard page will now show 2-3 tabs, depening on if the custom scoreboard option is enabled.

![Score board](imgs/Scoreboard.png)

The first tab will show the scoreboard of the teams who have the matching attribute.

The second tab will show the scoreboard of the teams who do not have the matching attribtue.

Finally, the optional 3rd tab will show the custom scoreboard.
![Custom scoreboard](imgs/Customboard.png)
