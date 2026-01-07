<template>
  <div class="page">
    <section class="hero">
      <div>
        <p class="eyebrow">Observability / Data Platform</p>
        <h1>Dual-store data flow</h1>
        <p class="lede">
          Track raw ingestion in the Raw DB while computed metrics and reports live in the Metrics DB.
        </p>
        <el-button type="primary" @click="refresh">Ping API</el-button>
        <el-button type="text" @click="$router.push('/upload')">去上传</el-button>
      </div>
      <div class="pillars">
        <el-card shadow="hover">
          <div class="card-title">API status</div>
          <div class="card-value">{{ apiStatus }}</div>
          <div class="card-sub">{{ healthMessage }}</div>
        </el-card>
        <el-card shadow="hover">
          <div class="card-title">Datasets</div>
          <div class="card-value">{{ datasets.length }}</div>
          <div class="card-sub">demo placeholder</div>
        </el-card>
      </div>
    </section>

    <section class="grid">
      <el-card shadow="never" class="panel">
        <div slot="header" class="panel-header">
          <span>Recent datasets</span>
          <el-button type="text" @click="loadDatasets">Reload</el-button>
        </div>
        <el-table :data="datasets" height="260" border v-if="datasets.length">
          <el-table-column prop="datasetId" label="Dataset ID" width="200" />
          <el-table-column prop="name" label="Name" />
          <el-table-column prop="status" label="Status" width="120" />
        </el-table>
        <div v-else class="empty">No datasets loaded yet.</div>
      </el-card>
    </section>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'HomeView',
  data() {
    return {
      apiStatus: 'idle',
      healthMessage: '',
      datasets: []
    };
  },
  created() {
    this.refresh();
    this.loadDatasets();
  },
  methods: {
    async refresh() {
      this.apiStatus = 'loading';
      try {
        const { data } = await api.health();
        this.healthMessage = data;
        this.apiStatus = 'ready';
      } catch (err) {
        this.healthMessage = err?.message || 'unreachable';
        this.apiStatus = 'error';
      }
    },
    async loadDatasets() {
      try {
        const { data } = await api.listDatasets();
        this.datasets = data || [];
      } catch (err) {
        this.datasets = [];
        this.healthMessage = err?.message || 'failed to load datasets';
      }
    }
  }
};
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 12px;
  color: #94a3b8;
  margin: 0 0 4px;
}

.lede {
  margin: 0 0 16px;
  color: #cbd5e1;
}

.pillars {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.card-title {
  font-size: 12px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  margin-top: 4px;
}

.card-sub {
  color: #cbd5e1;
  font-size: 13px;
  margin-top: 4px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
}

.panel {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.empty {
  padding: 16px;
  color: #94a3b8;
  text-align: center;
}
</style>
