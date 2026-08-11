# Privacy Policy for 𝕏. / Discord OmniBot

Effective date: August 11, 2026  
Last updated: August 11, 2026

This Privacy Policy explains how the Discord application **𝕏.**, also described as **Discord OmniBot** (Discord application ID `1264424150664089611`), accesses, uses, shares, stores, and deletes data when it is installed in or used from a Discord server or direct message.

## Data the app accesses

Discord may provide the app with data needed to operate its features, including:

- Message content, embeds, attachments, and related message metadata for messages the app is permitted to access.
- Basic account information attached to an interaction, message, or reaction, such as a Discord user ID, display name, and avatar.
- Server, channel, message, and reaction identifiers required to send responses and manage reaction controls.
- Command text and parameters supplied by users.

The app processes new messages in real time. It does not fetch or archive Discord message history, guild member lists, or user presence/activity data.

## How the data is used

The app uses Discord data only to provide its documented features:

- Detect supported X/Twitter, TikTok, and Instagram links and replace them with embed-compatible links.
- Preserve the posting user's display name, remaining message text, and attachments when replacing a supported link.
- Process `!`-prefixed commands and return requested utility, cryptocurrency, FFXIV market, and Dalamud information.
- Associate bot responses with the requesting user so that reaction-based deletion and pagination controls work.
- Parse specially formatted cryptocurrency alerts from one configured channel.
- Diagnose operational errors and count corrected links.

The app does not sell Discord data, use it for advertising, profile Discord users, or use Discord data to train artificial-intelligence or machine-learning models.

## Data stored outside Discord

The app stores or temporarily holds the following data on the computer where it runs:

- A corrected-link log containing the time of correction, the author's display name, and the original supported social-media URL.
- In-memory associations between Discord user IDs and bot message IDs for requester-only reaction controls.
- In-memory pagination/search state used for FFXIV results.
- Up to ten parsed cryptocurrency alert records per ticker, which may include the source alert text and timestamp.
- Attachments from a corrected-link message temporarily while they are downloaded and reposted to Discord.

The app does not maintain a database of complete Discord messages or member profiles.

## Data retention

- Temporary attachments are held only long enough to repost them to Discord.
- In-memory data is discarded when the app restarts. Some user-ID/message-ID associations may remain in memory until the corresponding bot response is deleted or the app restarts.
- Corrected-link log entries currently have no automatic expiration and remain until the operator removes them or fulfills a valid deletion request.
- Data will also be deleted when Discord or the affected user validly requests deletion, when it is no longer needed for the app's stated functionality, or when operation of the app ends, unless retention is legally required.

## Third-party services

The app uses the following services to provide requested features:

- **Discord** to receive events and send or manage messages.
- **fixupx.com** and **fxtwitter.com** for embed-compatible X/Twitter links.
- **vxtiktok.com** for embed-compatible TikTok links.
- **ddinstagram.com** for embed-compatible Instagram links.
- **Universalis** for FFXIV market data.
- **Coinbase** for cryptocurrency spot-price data.
- **Kamori** for current Dalamud release metadata.

When a feature calls one of these services, the relevant URL, item identifier, market symbol, or other request parameter is sent to that service. These providers process data under their own terms and privacy policies. The app does not authorize them to use Discord data for unrelated purposes.

## Data sharing

The app does not sell or rent Discord data. Data is shared only:

- With the service providers identified above as necessary to perform a requested or configured feature.
- When a user directs the app to repost content within Discord.
- When required by applicable law, regulation, or a valid legal process.
- When required to investigate security incidents, abuse, or violations of applicable terms.

## Choices and data requests

The current app does not provide a per-user command that prevents real-time processing of messages in channels the app can access. Server administrators can restrict the app to selected channels or remove it from the server. Users can also avoid direct-message interactions with the app.

To request access to or deletion of stored data, open a request through the [Discord OmniBot issue tracker](https://github.com/xa-io/discord-omnibot/issues). Do not include private message content, credentials, or other sensitive information in a public issue. Provide only enough non-sensitive context to allow the operator to arrange verification and fulfillment of the request.

Because the corrected-link log records display names rather than Discord user IDs, a requester may need to provide the display name used at the time and an approximate date or server context so matching entries can be located.

## Security

The operator limits access to stored app data to people who need it to operate and maintain the app. Reasonable measures are used to protect the runtime environment, but no method of storage or transmission can be guaranteed to be completely secure.

## Children's privacy

The app is intended only for people who are permitted to use Discord under Discord's terms and applicable law. The app is not knowingly directed to children below Discord's minimum permitted age.

## Changes to this policy

This policy may be updated when the app's features or data practices change. The effective and last-updated dates above will be revised when material changes are made. Continued use after an update is subject to the current published policy.

## Contact

Privacy questions and data requests can be submitted through the [Discord OmniBot issue tracker](https://github.com/xa-io/discord-omnibot/issues). Do not post secrets or sensitive personal information in a public issue.

