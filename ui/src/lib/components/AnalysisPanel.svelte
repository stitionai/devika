<script>
  import { onMount } from "svelte";
  import { selectedProject } from "$lib/store";
  import { API_BASE_URL } from "$lib/api";
  import * as Tabs from "$lib/components/ui/tabs";
  import { toast } from "svelte-sonner";

  let analysisResults = {
    codeReview: null,
    securityAudit: null,
    performanceAnalysis: null,
    dependencyAnalysis: null
  };

  let isAnalyzing = {
    codeReview: false,
    securityAudit: false,
    performanceAnalysis: false,
    dependencyAnalysis: false,
    generateTests: false,
    generateDocs: false
  };

  function validateProject() {
    if (!$selectedProject || $selectedProject === 'select project') {
      toast.error("Please select a project first");
      return false;
    }
    return true;
  }

  async function makeApiCall(endpoint, data, analysisType) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: $selectedProject,
          base_model: localStorage.getItem("selectedModel") || "gpt-3.5-turbo",
          ...data
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`${analysisType} error:`, error);
      throw error;
    }
  }

  async function runCodeReview() {
    if (!validateProject()) return;

    isAnalyzing.codeReview = true;
    try {
      const data = await makeApiCall("/api/code-review", { review_type: "comprehensive" }, "Code review");
      
      if (data.status === "success") {
        analysisResults.codeReview = data.review;
        toast.success("Code review completed");
      } else {
        toast.error(data.message || "Code review failed");
      }
    } catch (error) {
      toast.error(`Code review failed: ${error.message}`);
    } finally {
      isAnalyzing.codeReview = false;
    }
  }

  async function runSecurityAudit() {
    if (!validateProject()) return;

    isAnalyzing.securityAudit = true;
    try {
      const data = await makeApiCall("/api/security-audit", { audit_type: "comprehensive" }, "Security audit");
      
      if (data.status === "success") {
        analysisResults.securityAudit = data.audit;
        toast.success("Security audit completed");
      } else {
        toast.error(data.message || "Security audit failed");
      }
    } catch (error) {
      toast.error(`Security audit failed: ${error.message}`);
    } finally {
      isAnalyzing.securityAudit = false;
    }
  }

  async function runPerformanceAnalysis() {
    if (!validateProject()) return;

    isAnalyzing.performanceAnalysis = true;
    try {
      const data = await makeApiCall("/api/performance-analysis", { performance_metrics: "" }, "Performance analysis");
      
      if (data.status === "success") {
        analysisResults.performanceAnalysis = data.analysis;
        toast.success("Performance analysis completed");
      } else {
        toast.error(data.message || "Performance analysis failed");
      }
    } catch (error) {
      toast.error(`Performance analysis failed: ${error.message}`);
    } finally {
      isAnalyzing.performanceAnalysis = false;
    }
  }

  async function runDependencyAnalysis() {
    if (!validateProject()) return;

    isAnalyzing.dependencyAnalysis = true;
    try {
      const data = await makeApiCall("/api/dependency-analysis", {}, "Dependency analysis");
      
      if (data.status === "success") {
        analysisResults.dependencyAnalysis = data.analysis;
        toast.success("Dependency analysis completed");
      } else {
        toast.error(data.message || "Dependency analysis failed");
      }
    } catch (error) {
      toast.error(`Dependency analysis failed: ${error.message}`);
    } finally {
      isAnalyzing.dependencyAnalysis = false;
    }
  }

  async function generateTests() {
    if (!validateProject()) return;

    isAnalyzing.generateTests = true;
    try {
      const data = await makeApiCall("/api/generate-tests", { test_type: "unit" }, "Test generation");
      
      if (data.status === "success") {
        toast.success(`Tests generated successfully (${data.test_count || 'multiple'} files)`);
      } else {
        toast.error(data.message || "Test generation failed");
      }
    } catch (error) {
      toast.error(`Test generation failed: ${error.message}`);
    } finally {
      isAnalyzing.generateTests = false;
    }
  }

  async function generateDocumentation() {
    if (!validateProject()) return;

    isAnalyzing.generateDocs = true;
    try {
      const data = await makeApiCall("/api/generate-documentation", { doc_type: "comprehensive" }, "Documentation generation");
      
      if (data.status === "success") {
        toast.success(`Documentation generated successfully (${data.doc_count || 'multiple'} files)`);
      } else {
        toast.error(data.message || "Documentation generation failed");
      }
    } catch (error) {
      toast.error(`Documentation generation failed: ${error.message}`);
    } finally {
      isAnalyzing.generateDocs = false;
    }
  }

  function getSeverityColor(severity) {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-600';
      case 'high': return 'text-red-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-blue-500';
      default: return 'text-gray-500';
    }
  }

  function getPriorityColor(priority) {
    switch (priority?.toLowerCase()) {
      case 'critical': return 'text-red-600';
      case 'high': return 'text-red-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-blue-500';
      default: return 'text-gray-500';
    }
  }

  function clearResults() {
    analysisResults = {
      codeReview: null,
      securityAudit: null,
      performanceAnalysis: null,
      dependencyAnalysis: null
    };
    toast.info("Analysis results cleared");
  }

  // Clear results when project changes
  $: if ($selectedProject) {
    clearResults();
  }
</script>

<div class="w-full h-full flex flex-col border-[3px] rounded-xl overflow-hidden border-window-outline bg-background">
  <div class="flex items-center justify-between p-3 border-b bg-secondary">
    <h2 class="text-lg font-semibold">Code Analysis & Tools</h2>
    <button 
      on:click={clearResults}
      class="text-sm px-2 py-1 rounded hover:bg-background transition-colors"
      title="Clear all results"
    >
      <i class="fas fa-trash"></i>
    </button>
  </div>

  <div class="flex-1 overflow-y-auto p-4">
    <Tabs.Root value="analysis" class="w-full">
      <Tabs.List class="grid w-full grid-cols-3">
        <Tabs.Trigger value="analysis">Analysis</Tabs.Trigger>
        <Tabs.Trigger value="tools">Tools</Tabs.Trigger>
        <Tabs.Trigger value="results">Results</Tabs.Trigger>
      </Tabs.List>

      <Tabs.Content value="analysis" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <button
            on:click={runCodeReview}
            disabled={isAnalyzing.codeReview}
            class="p-4 border rounded-lg hover:bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="flex items-center gap-2">
              <i class="fas fa-search text-blue-500"></i>
              <span>Code Review</span>
              {#if isAnalyzing.codeReview}
                <i class="fas fa-spinner fa-spin"></i>
              {/if}
            </div>
            <p class="text-sm text-gray-500 mt-1">Analyze code quality and best practices</p>
          </button>

          <button
            on:click={runSecurityAudit}
            disabled={isAnalyzing.securityAudit}
            class="p-4 border rounded-lg hover:bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="flex items-center gap-2">
              <i class="fas fa-shield-alt text-red-500"></i>
              <span>Security Audit</span>
              {#if isAnalyzing.securityAudit}
                <i class="fas fa-spinner fa-spin"></i>
              {/if}
            </div>
            <p class="text-sm text-gray-500 mt-1">Identify security vulnerabilities</p>
          </button>

          <button
            on:click={runPerformanceAnalysis}
            disabled={isAnalyzing.performanceAnalysis}
            class="p-4 border rounded-lg hover:bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="flex items-center gap-2">
              <i class="fas fa-tachometer-alt text-green-500"></i>
              <span>Performance Analysis</span>
              {#if isAnalyzing.performanceAnalysis}
                <i class="fas fa-spinner fa-spin"></i>
              {/if}
            </div>
            <p class="text-sm text-gray-500 mt-1">Optimize code performance</p>
          </button>

          <button
            on:click={runDependencyAnalysis}
            disabled={isAnalyzing.dependencyAnalysis}
            class="p-4 border rounded-lg hover:bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="flex items-center gap-2">
              <i class="fas fa-cubes text-purple-500"></i>
              <span>Dependency Analysis</span>
              {#if isAnalyzing.dependencyAnalysis}
                <i class="fas fa-spinner fa-spin"></i>
              {/if}
            </div>
            <p class="text-sm text-gray-500 mt-1">Check dependencies and licenses</p>
          </button>
        </div>
      </Tabs.Content>

      <Tabs.Content value="tools" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <button
            on:click={generateTests}
            disabled={isAnalyzing.generateTests}
            class="p-4 border rounded-lg hover:bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="flex items-center gap-2">
              <i class="fas fa-vial text-blue-500"></i>
              <span>Generate Tests</span>
              {#if isAnalyzing.generateTests}
                <i class="fas fa-spinner fa-spin"></i>
              {/if}
            </div>
            <p class="text-sm text-gray-500 mt-1">Create unit and integration tests</p>
          </button>

          <button
            on:click={generateDocumentation}
            disabled={isAnalyzing.generateDocs}
            class="p-4 border rounded-lg hover:bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="flex items-center gap-2">
              <i class="fas fa-book text-green-500"></i>
              <span>Generate Docs</span>
              {#if isAnalyzing.generateDocs}
                <i class="fas fa-spinner fa-spin"></i>
              {/if}
            </div>
            <p class="text-sm text-gray-500 mt-1">Create comprehensive documentation</p>
          </button>
        </div>
      </Tabs.Content>

      <Tabs.Content value="results" class="space-y-4">
        {#if analysisResults.codeReview}
          <div class="border rounded-lg p-4">
            <h3 class="font-semibold mb-2 flex items-center gap-2">
              <i class="fas fa-search text-blue-500"></i>
              Code Review Results
            </h3>
            <div class="space-y-2">
              <p><strong>Score:</strong> {analysisResults.codeReview.review?.overall_score || 'N/A'}/10</p>
              <p><strong>Summary:</strong> {analysisResults.codeReview.review?.summary || 'No summary available'}</p>
              
              {#if analysisResults.codeReview.review?.issues?.length > 0}
                <div>
                  <strong>Issues ({analysisResults.codeReview.review.issues.length}):</strong>
                  <ul class="list-disc list-inside mt-1 space-y-1 max-h-32 overflow-y-auto">
                    {#each analysisResults.codeReview.review.issues.slice(0, 5) as issue}
                      <li class={getSeverityColor(issue.severity)}>
                        <strong>{issue.severity}:</strong> {issue.description}
                      </li>
                    {/each}
                    {#if analysisResults.codeReview.review.issues.length > 5}
                      <li class="text-gray-500">... and {analysisResults.codeReview.review.issues.length - 5} more</li>
                    {/if}
                  </ul>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        {#if analysisResults.securityAudit}
          <div class="border rounded-lg p-4">
            <h3 class="font-semibold mb-2 flex items-center gap-2">
              <i class="fas fa-shield-alt text-red-500"></i>
              Security Audit Results
            </h3>
            <div class="space-y-2">
              <p><strong>Security Score:</strong> {analysisResults.securityAudit.security_score || 'N/A'}/10</p>
              <p><strong>Risk Level:</strong> 
                <span class={getPriorityColor(analysisResults.securityAudit.overall_risk)}>
                  {analysisResults.securityAudit.overall_risk?.toUpperCase() || 'Unknown'}
                </span>
              </p>
              
              {#if analysisResults.securityAudit.vulnerabilities?.length > 0}
                <div>
                  <strong>Vulnerabilities ({analysisResults.securityAudit.vulnerabilities.length}):</strong>
                  <ul class="list-disc list-inside mt-1 space-y-1 max-h-32 overflow-y-auto">
                    {#each analysisResults.securityAudit.vulnerabilities.slice(0, 5) as vuln}
                      <li class={getSeverityColor(vuln.severity)}>
                        <strong>{vuln.severity}:</strong> {vuln.title}
                      </li>
                    {/each}
                    {#if analysisResults.securityAudit.vulnerabilities.length > 5}
                      <li class="text-gray-500">... and {analysisResults.securityAudit.vulnerabilities.length - 5} more</li>
                    {/if}
                  </ul>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        {#if analysisResults.performanceAnalysis}
          <div class="border rounded-lg p-4">
            <h3 class="font-semibold mb-2 flex items-center gap-2">
              <i class="fas fa-tachometer-alt text-green-500"></i>
              Performance Analysis Results
            </h3>
            <div class="space-y-2">
              <p><strong>Performance Score:</strong> {analysisResults.performanceAnalysis.analysis?.overall_performance_score || 'N/A'}/10</p>
              
              {#if analysisResults.performanceAnalysis.analysis?.bottlenecks?.length > 0}
                <div>
                  <strong>Bottlenecks ({analysisResults.performanceAnalysis.analysis.bottlenecks.length}):</strong>
                  <ul class="list-disc list-inside mt-1 space-y-1 max-h-32 overflow-y-auto">
                    {#each analysisResults.performanceAnalysis.analysis.bottlenecks.slice(0, 5) as bottleneck}
                      <li class={getPriorityColor(bottleneck.impact)}>
                        <strong>{bottleneck.impact}:</strong> {bottleneck.issue}
                      </li>
                    {/each}
                    {#if analysisResults.performanceAnalysis.analysis.bottlenecks.length > 5}
                      <li class="text-gray-500">... and {analysisResults.performanceAnalysis.analysis.bottlenecks.length - 5} more</li>
                    {/if}
                  </ul>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        {#if analysisResults.dependencyAnalysis}
          <div class="border rounded-lg p-4">
            <h3 class="font-semibold mb-2 flex items-center gap-2">
              <i class="fas fa-cubes text-purple-500"></i>
              Dependency Analysis Results
            </h3>
            <div class="space-y-2">
              <p><strong>Total Dependencies:</strong> {analysisResults.dependencyAnalysis.dependencies?.total_count || 'Unknown'}</p>
              <p><strong>Vulnerable Packages:</strong> 
                <span class="text-red-500">
                  {analysisResults.dependencyAnalysis.security_summary?.total_vulnerable_packages || 0}
                </span>
              </p>
              
              {#if analysisResults.dependencyAnalysis.recommendations?.length > 0}
                <div>
                  <strong>Critical Actions:</strong>
                  <ul class="list-disc list-inside mt-1 space-y-1 max-h-32 overflow-y-auto">
                    {#each analysisResults.dependencyAnalysis.recommendations.filter(r => r.priority === 'critical' || r.priority === 'high').slice(0, 5) as rec}
                      <li class={getPriorityColor(rec.priority)}>
                        <strong>{rec.priority}:</strong> {rec.description}
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        {#if !analysisResults.codeReview && !analysisResults.securityAudit && !analysisResults.performanceAnalysis && !analysisResults.dependencyAnalysis}
          <div class="text-center text-gray-500 py-8">
            <i class="fas fa-chart-bar text-4xl mb-4"></i>
            <p>No analysis results yet. Run an analysis to see results here.</p>
          </div>
        {/if}
      </Tabs.Content>
    </Tabs.Root>
  </div>
</div>