import { test, expect } from "@playwright/experimental-ct-react";

test("test mínimo - div simple", async ({ mount }) => {
  const component = await mount(<div data-testid="hello">Hello</div>);
  await expect(component.getByTestId("hello")).toBeVisible();
});
