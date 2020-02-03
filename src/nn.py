import os
import numpy as np
import tensorflow as tf

from tqdm import tqdm
from tensorflow.keras import layers


class Logger():
    def __init__(self, log_dir):
        self.writer = tf.summary.create_file_writer(log_dir)
        
    def write(self, var_name, metric, step):
        with self.writer.as_default():
            tf.summary.scalar(var_name, metric.result(), step)
        metric.reset_states()


class Model(tf.keras.Model):
    def __init__(self, n_inputs, layer_sizes, n_outputs):
        super().__init__()

        nn_layers = tf.keras.Sequential()
        nn_layers.add(layers.Dense(n_inputs))
        
        for size in layer_sizes:
            nn_layers.add(layers.Dense(size))
            nn_layers.add(layers.LeakyReLU())
            
        nn_layers.add(layers.Dense(n_outputs))

        self.nn = nn_layers

    def call(self, inputs):
        return self.nn(inputs)


class Trainer:
    def __init__(self, attacker_model, defender_model, \
                attacker_loss_fn, defender_loss_fn, \
                attacker_optimizer, defender_optimizer, \
                working_dir, logging=False):

        self.attacker = attacker_model
        self.defender = defender_model
        self.attacker_loss_fn = attacker_loss_fn
        self.defender_loss_fn = defender_loss_fn
        self.attacker_optimizer = attacker_optimizer
        self.defender_optimizer = defender_optimizer

        self.checkpoint_path = os.path.join(working_dir, 'ckpt')
        self.checkpoint = tf.train.Checkpoint(attacker=attacker, defender=defender, \
                                            attacker_optimizer=attacker_optimizer, \
                                            defender_optimizer=defender_optimizer)

        self.logger = Logger(working_dir) if logging else None
        
        if self.logger:
            self.metric_loss = tf.keras.metrics.Mean()
            self.metric_rho = tf.keras.metrics.Mean()

    def train_step(self): #TODO
        with tf.GradientTape() as tape:
            # Get current predictions of network
            y_pred = self.model(np.array([[0,0]]), training=True)
           
            # Calculate loss generated by predictions
            loss = self.loss_function(TARGET, y_pred)
            
            self.metric_loss.update_state(loss)
            self.metric_acc.update_state(TARGET, 0)

        gradients = tape.gradient(loss, self.model.trainable_variables)
        # Change trainable variable values according to gradient by applying optimizer policy
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        
        #self.train_loss(loss)

    def train(self, n_steps, n_episodes, simulation_horizon): #TODO
        # generazione ambiente iniziale
        for i in range(n_steps):
            # for episode
                # selezione selta attaccante
                # update modello (?)
                # selezione scelta difensore
                # simulazione h passi
                
            # training sul dataset
            # scelta azione concreta
            self.train_step(simulation_horizon)

    def test_step(self): #TODO
        self.test_loss(self.loss_function(y, self.model(x)))

    def test(self, n_steps): #TODO
        for _ in range(n_steps):
            self.test_step()

    def run(self, n_epochs, n_steps, n_episodes, simulation_horizon=100):
        epochs = tqdm(range(n_epochs)) if self.logger else range(n_epochs)
        
        for i in epochs:
            self.train(n_episodes, n_steps, simulation_horizon)
            
            if (i + 1) % 10:
                self.checkpoint.save(file_prefix=self.checkpoint_path)
            
            if self.logger:
                pass #log rho

            

EPISODES = 500
EPOCHS = 1000

TARGET = 10

#tf.autograph.set_verbosity(1)

attacker = Model(2, [4], 1)
defender = Model(2, [4], 1)
optimizer = tf.keras.optimizers.Adam(1e-4)
loss = tf.keras.losses.MeanSquaredError()

trainer = Trainer(attacker, defender, loss, loss, optimizer, optimizer, '/tmp/test_tf')

#for i in tqdm(range(EPOCHS)):
#    trainer.train()
    #trainer.test(dataset)
#    if i % 10 == 0:
#        logger.write('loss', trainer.metric_loss, step=i)
#        logger.write('acc', trainer.metric_acc, step=i)
