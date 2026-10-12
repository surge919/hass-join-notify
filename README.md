# Join by Joaoapps Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)

A custom HACS integration for Home Assistant that connects with [Join by Joaoapps](https://joaoapps.com/join/). This integration automatically discovers your registered Join devices and exposes them as native Home Assistant notification entities (`notify.join_<device_name>`).

---

## Features

- **UI Config Flow Setup**: Configure your Join API Key once via the Home Assistant UI without touching `configuration.yaml`.
- **Auto-Discovery**: Automatically queries Join's registration API to create notification entities for all your registered devices (e.g., Pixel 10a, Shield TV, Basement, etc.).
- **Group Notifications**: Automatically creates a "Join All" entity (`notify.join_all`) to push notifications to all devices in your account simultaneously.
- **Modern Notification Service**: Fully supports Home Assistant's unified `notify.send_message` action syntax.

---

## Installation via HACS

1. Open **HACS** in your Home Assistant sidebar and go to **Integrations**.
2. Click the **3 dots** in the top-right corner and choose **Custom repositories**.
3. Add the following repository details:
   - **Repository**: `https://github.com/surge919/hass-join-notify`
   - **Type**: `Integration`
4. Click **Add**, find **Join by Joaoapps** in the list, and click **Download**.
5. Restart Home Assistant (**Developer Tools > YAML > Restart**).

---

## Configuration

1. Get your Join API Key from the [Join Web Portal](https://joinjoaomgcd.appspot.com/).
2. In Home Assistant, go to **Settings > Devices & Services**.
3. Click **Add Integration** in the bottom right corner.
4. Search for **Join by Joaoapps** (or **Join**).
5. Paste your **API Key** and click **Submit**.

![Join API Key Setup](./images/Screenshot%20From%202026-10-11%2020-25-45.png)

6. Once submitted, the integration entry will be created under **Devices & Services**:

![Join Integration Entry](./images/Screenshot%20From%202026-10-11%2020-27-23.png)

---

## Discovered Entities

Upon setup, all registered Join devices under your account are automatically imported as notification entities:

![Discovered Entities](./images/Screenshot%20From%202026-10-11%2020-28-00.png)

---

## Usage

Once configured, your Join devices will appear as `notify` entities. You can trigger them using the standard `notify.send_message` action in automations, scripts, or Developer Tools.

### Example: Target a Specific Device via UI Action

In **Developer Tools > Actions**:
- **Action**: `Send a notification message` (`notify.send_message`)
- **Target**: Select `notify.join_pixel_10a` or `notify.join_shieldtv_bedroom`
- **Title**: `Front Door`
- **Message**: `Front door motion detected!`

### Example: Target in YAML Automations

```yaml
alias: Send Join Notification on Door State Change
trigger:
  - trigger: state
    entity_id: lock.front_front_door
    to: locked
    id: locked
  - trigger: state
    entity_id: lock.front_front_door
    to: unlocked
    id: unlocked
action:
  - action: notify.send_message
    target:
      entity_id: notify.join_pixel_10a
    data:
      title: "{{ state_attr('lock.front_front_door', 'friendly_name') or 'Front Door Lock' }}"
      message: >-
        {% if trigger is defined %}
          {{ 'Locked' if trigger.id == 'locked' else 'Unlocked' }} by {{
          state_attr('lock.front_front_door', 'changed_by') or 'unknown' }}.
        {% else %}
          Manual test trigger.
        {% endif %}
        Battery {{ states('sensor.front_front_door_battery_level') }}%
