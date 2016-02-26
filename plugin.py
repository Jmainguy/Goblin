###
# Copyright (c) 2016, Jonathan Mainguy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import random
import re
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Goblin')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Goblin(callbacks.Plugin):
    """Fight a goblin"""
    threaded = True
    def __init__(self, irc):
        self.__parent = super(Goblin, self)
        self.__parent.__init__(irc)

    def _diceroll(self, dice, sides):
        results = []
        die = 1
        while (die <= dice):
            result = random.randint(1, sides)
            results.append(result)
            die = die + 1
        return results

    def _diceresults(self, dice, defaultDiceResults):
        # Get dice, and sides
        dice, sides = dice.split("d")
        # Roll them
        results = self._diceroll(int(dice), int(sides))
        # Add results to list
        for result in results:
            defaultDiceResults.append(result)

    def roll(self, irc, junk, junk2, args):
        """roll the dice"""

        # Parse the output
        # Create the blank list we will use
        positiveDice = []
        negativeDice = []
        positiveModifier = []
        negativeModifier = []
        # Set the default list for dice and modifiers as positive
        defaultDice = positiveDice
        defaultModifier = positiveModifier
        # How many args?
        argsleft = len(args)
        # What does a dice arg look like
        dicearg = re.compile("^([0-9]+d[0-9]+)$")
        # What does a modifer arg look like
        modifierarg = re.compile("^([0-9]+)$")
        # Loop through and process each arg, placing in appropriate lists
        while argsleft > 0:
            arg = args[0]
            if dicearg.match(arg):
                defaultDice.append(arg)
            elif modifierarg.match(arg):
                defaultModifier.append(int(arg))
            elif arg == '+':
                defaultModifier = positiveModifier
                defaultDice = positiveDice
            elif arg == '-':
                defaultModifier = negativeModifier
                defaultDice = negativeDice
            args.pop(0)
            argsleft = argsleft - 1

        # Create list for positive and negative dice results
        positiveDiceResults = []
        negativeDiceResults = []
        # Roll the dice, and add to appropriate list
        for dice in positiveDice:
            defaultDiceResults = positiveDiceResults
            self._diceresults(dice, defaultDiceResults)
        for dice in negativeDice:
            defaultDiceResults = negativeDiceResults
            self._diceresults(dice, defaultDiceResults)
        # Start with a blank message and add on to it as needed
        msg = ''
        # Empty math list
        mathlist = []
        # Sum of positive rolls
        if positiveDiceResults:
            pdrtotal = sum(positiveDiceResults)
            mathlist.append(pdrtotal)
            if len(positiveDiceResults) > 1:
                msg = msg + "You rolled " + str(positiveDiceResults)
            else:
                msg = msg + "You rolled a " + str(positiveDiceResults[0])
        # Sum of positive modifiers
        if positiveModifier:
            pmtotal = sum(positiveModifier)
            mathlist.append(pmtotal)
            msg = msg + " + positive modifiers of " + str(pmtotal)
        # Sum of negative rolls
        if negativeDiceResults:
            ndrtotal = sum(negativeDiceResults)
            mathlist.append(-ndrtotal)
            if len(negativeDiceResults) > 1:
                msg = msg + " - negative rolls of " + str(negativeDiceResults)
            else:
                msg = msg + " - negative roll of " + str(negativeDiceResults)
        # Sum of negative modifiers
        if negativeModifier:
            nmtotal = sum(negativeModifier)
            mathlist.append(-nmtotal)
            msg = msg + " - negative modifiers of " + str(nmtotal)
        # Send the long message with all the above
        irc.reply(msg)
        # Do the math, and send the total
        total = sum(mathlist)
        irc.reply("For a total of %s" % total)

    roll = wrap(roll, [any('something')])


Class = Goblin

# vim:set shiftwidth=4 tabstop=4 expandtab:
