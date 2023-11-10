from tensorflow import keras

"""
SCRIPT FOR AI

NN SHAPE
INPUTS (x11): 
Ray Distance x8
Reward_distance
player_angle
player_speed

OUTPUTS(x4):
FORWARD
RIGHT
LEFT
BACK
"""



def initialise_NN_for_player():
    """
    Script which initialises the NN for a player
    SIZE: [11, N, 4]
    :return: TensorFlow model
    """
    model = keras.models.Sequential([
    keras.layers.Flatten(input_shape=11),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(10)
    ])



"""
async def main():

    await asyncio.gather(
        asyncio.to_thread(GAME_OBJ.main()),
        print_something()
    )


async def print_something():
    print("hi")

asyncio.run(main())
"""