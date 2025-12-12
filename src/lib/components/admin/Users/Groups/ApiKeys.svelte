<script lang="ts">
	import { getContext } from 'svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { getConnectionsConfig } from '$lib/apis/configs';
	import { onMount, tick } from 'svelte';

	const i18n = getContext('i18n');

	export let data = {};

	let connectionType = 'openai';
	let url = '';
	let authType = 'bearer';
	let token = '';
	let useDefault = true;

	// Default connection config from admin settings
	let defaultConfig = null;
	
	// Flag to prevent reactive loop when updating data.api_config
	let isUpdatingFromUser = false;
	let isInitialized = false;
	let userExplicitlySetUseDefault = false; // Track if user explicitly toggled useDefault

	onMount(async () => {
		try {
			defaultConfig = await getConnectionsConfig(localStorage.token);
		} catch (error) {
			console.error('Failed to load default connection config:', error);
		}
		init();
		// Initialize previousFieldValues after init to prevent immediate reactive update
		previousFieldValues = `${useDefault}-${connectionType}-${url}-${authType}-${token}`;
		isInitialized = true;
	});

	const init = () => {
		if (isUpdatingFromUser) return; // Don't init if we're in the middle of a user update
		if (userExplicitlySetUseDefault) return; // Don't override user's explicit choice
		
		if (data?.api_config && Object.keys(data.api_config).length > 0) {
			const apiConfig = data.api_config;
			connectionType = apiConfig.connection_type || 'openai';
			url = apiConfig.url || '';
			authType = apiConfig.auth_type || 'bearer';
			token = apiConfig.token || '';
			useDefault = !apiConfig.url; // If URL is not set, use default
		} else {
			useDefault = true;
		}
	};

	// Track when user explicitly toggles useDefault
	function handleUseDefaultChange() {
		userExplicitlySetUseDefault = true;
		// Set flag before making changes to prevent reactive statement from triggering
		isUpdatingFromUser = true;
		// When toggling to custom (useDefault = false), initialize URL if empty
		if (!useDefault && url === '') {
			if (defaultConfig && defaultConfig.length > 0) {
				const firstConfig = defaultConfig[0];
				if (firstConfig.url) {
					url = firstConfig.url;
				}
				if (firstConfig.connection_type) {
					connectionType = firstConfig.connection_type;
				}
				if (firstConfig.auth_type) {
					authType = firstConfig.auth_type;
				}
			} else {
				// If no default config, set a placeholder URL to prevent init() from resetting useDefault
				url = 'https://api.openai.com/v1';
			}
		}
		// Update data config immediately
		updateDataConfigSync();
		// Reset flag after update
		tick().then(() => {
			isUpdatingFromUser = false;
		});
	}

	// Track previous values to detect external data changes
	let previousApiConfig = null;
	let previousFieldValues = '';

	// Only init when data changes from external source (not from our own updates)
	$: if (data && isInitialized && !userExplicitlySetUseDefault) {
		const currentApiConfig = JSON.stringify(data?.api_config || {});
		if (currentApiConfig !== previousApiConfig) {
			// Only init if the change came from outside (not from our update)
			if (!isUpdatingFromUser) {
				init();
			}
			previousApiConfig = currentApiConfig;
		}
	}

	// Function to update data config - check flag inside function, not in reactive condition
	function updateDataConfigSync() {
		if (!data || isUpdatingFromUser) return;
		if (!data.api_config) {
			data.api_config = {};
		}
		if (useDefault) {
			// Clear group-specific config to use defaults
			data.api_config = {};
		} else {
			data.api_config = {
				connection_type: connectionType,
				url: url,
				auth_type: authType,
				token: token
			};
		}
	}

	// Handle field changes with event handlers to avoid reactive cycles
	function handleFieldChange() {
		updateDataConfigSync();
	}

	// Update when any field changes - use a computed value to track changes
	$: fieldValues = `${useDefault}-${connectionType}-${url}-${authType}-${token}`;
	$: if (data && isInitialized) {
		if (fieldValues !== previousFieldValues) {
			previousFieldValues = fieldValues;
			updateDataConfigSync();
		}
	}
</script>

<div class="flex flex-col space-y-3">
	<div class="text-xs text-gray-500 dark:text-gray-400 mb-2">
		{$i18n.t(
			'Configure API connection settings for this group. If not set, the default connection configuration from admin settings will be used.'
		)}
	</div>

	<div class="flex flex-col w-full">
		<div class="flex items-center justify-between mb-2">
			<div class="text-xs font-medium">{$i18n.t('Use Default Connection')}</div>
			<label class="relative inline-flex items-center cursor-pointer">
				<input
					type="checkbox"
					class="sr-only peer"
					bind:checked={useDefault}
					on:change={handleUseDefaultChange}
				/>
				<div
					class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-gray-300 dark:peer-focus:ring-gray-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-gray-600 dark:peer-checked:bg-gray-600"
				></div>
			</label>
		</div>
	</div>

	{#if !useDefault}
		<div class="flex flex-col w-full">
			<div class="mb-1 text-xs text-gray-500">{$i18n.t('Connection Type')}</div>
			<select
				class="w-full text-sm bg-transparent border border-gray-200 dark:border-gray-700 rounded px-2 py-1 outline-hidden"
				bind:value={connectionType}
				on:change={handleFieldChange}
			>
				<option value="openai">OpenAI</option>
				<option value="ollama">Ollama</option>
			</select>
		</div>

		<div class="flex flex-col w-full">
			<div class="mb-1 text-xs text-gray-500">{$i18n.t('Connection URL')}</div>
			<input
				class="w-full text-sm bg-transparent border border-gray-200 dark:border-gray-700 rounded px-2 py-1 placeholder:text-gray-300 dark:placeholder:text-gray-700 outline-hidden"
				type="text"
				bind:value={url}
				on:input={handleFieldChange}
				placeholder={$i18n.t('e.g., https://api.openai.com/v1')}
			/>
		</div>

		<div class="flex flex-col w-full">
			<div class="mb-1 text-xs text-gray-500">{$i18n.t('Auth Type')}</div>
			<select
				class="w-full text-sm bg-transparent border border-gray-200 dark:border-gray-700 rounded px-2 py-1 outline-hidden"
				bind:value={authType}
				on:change={handleFieldChange}
			>
				<option value="bearer">Bearer Token</option>
				<option value="none">None</option>
				<option value="session">Session</option>
			</select>
		</div>

		{#if authType === 'bearer'}
			<div class="flex flex-col w-full">
				<div class="mb-1 text-xs text-gray-500">{$i18n.t('API Token')}</div>
				<SensitiveInput
					placeholder={$i18n.t('Enter API token')}
					bind:value={token}
					on:change={handleFieldChange}
				/>
			</div>
		{/if}
	{/if}
</div>

