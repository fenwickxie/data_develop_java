import Vue from 'vue';
import Vuex from 'vuex';
import api from '@/api';

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    apiStatus: 'idle',
    healthMessage: '',
    user: null,
    token: localStorage.getItem('jwt') || null,
    datasets: [],
    files: [],
    metrics: [],
    reports: []
  },
  mutations: {
    setApiStatus(state, status) {
      state.apiStatus = status;
    },
    setHealthMessage(state, message) {
      state.healthMessage = message;
    },
    setUser(state, user) {
      state.user = user;
    },
    setToken(state, token) {
      state.token = token;
      if (token) {
        localStorage.setItem('jwt', token);
      } else {
        localStorage.removeItem('jwt');
      }
    },
    setDatasets(state, datasets) {
      state.datasets = datasets;
    },
    setFiles(state, files) {
      state.files = files;
    },
    setMetrics(state, metrics) {
      state.metrics = metrics;
    },
    setReports(state, reports) {
      state.reports = reports;
    }
  },
  actions: {
    async pingHealth({ commit }) {
      commit('setApiStatus', 'loading');
      try {
        const { data } = await api.health();
        commit('setHealthMessage', data);
        commit('setApiStatus', 'ready');
      } catch (err) {
        commit('setHealthMessage', err?.message || 'unreachable');
        commit('setApiStatus', 'error');
      }
    },
    async login({ commit }, credentials) {
      const { data } = await api.login(credentials);
      commit('setToken', data.token);
      commit('setUser', { username: credentials.username });
    },
    logout({ commit }) {
      commit('setToken', null);
      commit('setUser', null);
    },
    async fetchDatasets({ commit }) {
      const { data } = await api.listDatasets();
      commit('setDatasets', data);
    },
    async fetchFiles({ commit }, datasetId) {
      const { data } = await api.listFiles(datasetId);
      commit('setFiles', data);
    },
    async fetchMetrics({ commit }, params) {
      const { data } = await api.listMetrics(params);
      commit('setMetrics', data);
    },
    async fetchReports({ commit }, params) {
      const { data } = await api.listReports(params);
      commit('setReports', data);
    }
  },
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user
  }
});

export default store;

