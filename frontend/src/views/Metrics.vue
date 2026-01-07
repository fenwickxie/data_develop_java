<template>
  <div class="metrics-page">
    <el-card shadow="hover">
      <div slot="header" class="panel-header">
        <span>指标列表</span>
        <div class="actions">
          <el-input v-model="datasetId" placeholder="datasetId" size="small" style="width:200px" />
          <el-input v-model="fileId" placeholder="fileId" size="small" style="width:200px" />
          <el-button type="primary" size="small" @click="loadMetrics" :loading="loading">查询</el-button>
        </div>
      </div>
      <el-table :data="metrics" v-loading="loading" height="380" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="metricName" label="名称" width="180" />
        <el-table-column prop="metricType" label="类型" width="120" />
        <el-table-column prop="datasetId" label="Dataset" width="160" />
        <el-table-column prop="fileId" label="File" width="160" />
        <el-table-column prop="metricValue" label="值" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'MetricsView',
  data() {
    return {
      datasetId: '',
      fileId: '',
      metrics: [],
      loading: false
    };
  },
  methods: {
    async loadMetrics() {
      this.loading = true;
      this.metrics = [];
      try {
        const params = {};
        if (this.datasetId) params.datasetId = this.datasetId;
        if (this.fileId) params.fileId = this.fileId;
        const { data } = await api.listMetrics(params);
        this.metrics = data || [];
      } catch (err) {
        this.metrics = [];
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.metrics-page {
  max-width: 1000px;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
