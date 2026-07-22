// @vitest-environment jsdom

import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import LandingPage from "./LandingPage.vue";

const summary = {
  coverage: {
    observations: 1025,
    states: 41,
    startYear: 2000,
    endYear: 2024,
  },
  pooledCorrelations: {
    temperatureYield: -0.171,
    precipitationYield: -0.04,
  },
  nationalStateAverageChange: {
    temperatureF: 2.36,
    yieldBuPerAcre: 28,
  },
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("LandingPage", () => {
  it("renders verified project facts and opens the dashboard", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: async () => summary })
    );
    const wrapper = mount(LandingPage);
    await flushPromises();

    expect(wrapper.text()).toContain("1,025");
    expect(wrapper.text()).toContain("Temperature–yield association");
    expect(wrapper.text()).toContain("-0.171");

    await wrapper.get("button.primary-action").trigger("click");
    expect(wrapper.emitted("explore-dashboard")).toHaveLength(1);
  });

  it("keeps the dashboard available when the summary request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    const wrapper = mount(LandingPage);
    await flushPromises();

    expect(wrapper.get('[role="status"]').text()).toContain(
      "summary is temporarily unavailable"
    );
    expect(wrapper.get("button.primary-action").exists()).toBe(true);
  });
});
