<template>
  <div class="reports-page">
    <el-card shadow="hover" class="mb16">
      <div slot="header" class="panel-header">
        <span>报表列表</span>
        <div class="actions">
          <el-input v-model="filters.datasetId" placeholder="datasetId" size="small" style="width:200px" />
          <el-input v-model="filters.fileId" placeholder="fileId" size="small" style="width:200px" />
          <el-button type="primary" size="small" @click="loadReports" :loading="loading">查询</el-button>
        </div>
      </div>
      <el-table :data="reports" v-loading="loading" height="300" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="reportType" label="类型" width="140" />
        <el-table-column prop="datasetId" label="Dataset" width="160" />
        <el-table-column prop="fileId" label="File" width="160" />
        <el-table-column prop="storageType" label="存储" width="120" />
        <el-table-column prop="bucket" label="Bucket" width="180" />
        <el-table-column prop="objectKey" label="Object Key" />
        <el-table-column prop="generatedAt" label="生成时间" width="200" />
        <el-table-column label="操作" width="120">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="viewReport(scope.row)" v-if="scope.row.objectKey">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="hover">
      <div slot="header">创建报表</div>
      <el-form label-width="100px" :model="form" label-position="left" class="report-form">
        <el-form-item label="Dataset">
          <el-input v-model="form.datasetId" placeholder="datasetId" />
        </el-form-item>
        <el-form-item label="File">
          <el-input v-model="form.fileId" placeholder="fileId" />
        </el-form-item>
        <el-form-item label="类型">
          <el-input v-model="form.reportType" placeholder="reportType" />
        </el-form-item>
        <el-form-item label="存储类型">
          <el-input v-model="form.storageType" placeholder="storageType" />
        </el-form-item>
        <el-form-item label="Bucket">
          <el-input v-model="form.bucket" placeholder="bucket" />
        </el-form-item>
        <el-form-item label="Object Key">
          <el-input v-model="form.objectKey" placeholder="objectKey" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="create" :loading="creating">提交</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
      <div v-if="message" class="result">{{ message }}</div>
    </el-card>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'ReportsView',
  data() {
    return {
      filters: {
        datasetId: '',
        fileId: ''
      },
      reports: [],
      loading: false,
      form: {
        datasetId: '',
        fileId: '',
        reportType: '',
        storageType: '',
        bucket: '',
        objectKey: ''
      },
      creating: false,
      message: ''
    };
  },
  methods: {
    async loadReports() {
      this.loading = true;
      this.message = '';
      try {
        const params = {};
        if (this.filters.datasetId) params.datasetId = this.filters.datasetId;
        if (this.filters.fileId) params.fileId = this.filters.fileId;
        const { data } = await api.listReports(params);
        this.reports = data || [];
      } catch (err) {
        this.reports = [];
        this.message = err?.message || '加载失败';
      } finally {
        this.loading = false;
      }
    },
    async create() {
      this.creating = true;
      this.message = '';
      try {
        const payload = { ...this.form };
        const { data } = await api.createReport(payload);
        this.message = `创建成功，ID: ${data.id}`;
        await this.loadReports();
      } catch (err) {
        this.message = err?.response?.data?.message || err?.message || '创建失败';
      } finally {
        this.creating = false;
      }
    },
    reset() {
      this.form = {
        datasetId: '',
        fileId: '',
        reportType: '',
        storageType: '',
        bucket: '',
        objectKey: ''
      };
      this.message = '';
    },
    viewReport(report) {
      // For demo: construct object storage URL (in production, use signed URL service)
      const baseUrl = process.env.VUE_APP_STORAGE_BASE_URL || 'https://objectstorage.region.oraclecloud.com';
      const url = `${baseUrl}/${report.bucket}/${report.objectKey}`;
      window.open(url, '_blank');
      this.message = `正在打开报表: ${report.objectKey}`;
    }
  }
};
</script>

<style scoped>
.reports-page {
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
.report-form {
  max-width: 520px;
}
.mb16 {
  margin-bottom: 16px;
}
.result {
  margin-top: 10px;
  word-break: break-all;
}
</style>
