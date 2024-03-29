#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 11:36:51 2018

@author: a4balakr
"""

import numpy as np

class evoReward():
    def __init__(self,
                 DNA_bound,
                 cross_rate,
                 mutation_rate,
                 pop_size,
                 obs_space_size,
                 action_size):
        self.DNA_bound = DNA_bound
        self.cross_rate = cross_rate
        self.mutate_rate = mutation_rate
        self.pop_size = pop_size
        self.fitness = np.zeros(pop_size)
        self.obs_space_size = obs_space_size
        self.action_size = action_size

        self.DNA_size = obs_space_size * action_size
        self.pop = np.random.randint(
            *DNA_bound, size=(pop_size, self.DNA_size)).astype(np.int8)

        self.num_agents_finished = 0
        self.rewards_ready = False
        self.num_agents_ready = 0

    def set_fitness(self, fitness):
        self.fitness = fitness
        self.normalize_fitness()

    def get_fitness(self):
        return self.fitness

    def normalize_fitness(self):
        ptp = np.ptp(self.fitness)
        if ptp != 0:
            self.fitness = (self.fitness - np.min(self.fitness)) / ptp

    def are_rewards_ready(self):
        return self.rewards_ready

    def notify_episode_start(self):
        self.num_agents_ready += 1
        if self.num_agents_ready == self.pop_size:
            self.rewards_ready = False
            self.num_agents_ready = 0

    def set_agent_fitness(self, fitness, agent_id):
        self.fitness[agent_id] = fitness
        self.num_agents_finished += 1

        if self.num_agents_finished == self.pop_size:
            self.normalize_fitness()
            self.rewards_ready = False
            self.evolve()
            self.num_agents_finished = 0
            self.rewards_ready = True

    def select(self):
        fitness = self.get_fitness(
        ) + 1e-4  # add a small amount to avoid all zero fitness
        idx = np.random.choice(
            np.arange(self.pop_size),
            size=self.pop_size,
            replace=True,
            p=fitness / fitness.sum())
        return self.pop[idx]

    def crossover(self, parent, pop):
        if np.random.rand() < self.cross_rate:
            i_ = np.random.randint(
                0, self.pop_size, size=1)  # select another individual from pop
            cross_points = np.random.randint(0, 2, self.DNA_size).astype(
                np.bool)  # choose crossover points
            parent[cross_points] = pop[
                i_, cross_points]  # mating and produce one child
        return parent

    def mutate(self, child):
        for point in range(self.DNA_size):
            if np.random.rand() < self.mutate_rate:
                child[point] = np.random.randint(
                    *self.DNA_bound)  # choose a random ASCII index
        return child

    def evolve(self):
        pop = self.select()
        pop_copy = pop.copy()
        for parent in pop:  # for every parent
            child = self.crossover(parent, pop_copy)
            child = self.mutate(child)
            parent[:] = child
        self.pop = pop

    def get_reward(self, dna_index, action, state):
        weight_matrix = self.pop[dna_index].reshape(
            self.action_size, self.obs_space_size)
        weights = weight_matrix[action]
        return np.sum(weights * state)

    def get_DNA(self, n):
        return self.pop[n].reshape((self.action_size, self.obs_space_size))
