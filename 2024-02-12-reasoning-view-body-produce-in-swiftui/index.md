---
title: "(Hidden Gem)? for SwiftUI View Updates Reasoning"
category: Programming
tags: [SwiftUI]
---

Reasoning SwiftUI's view updates is challenging. In WWDC 2021, Apple
introduced the concept of "dependency" to help developers understand
this process in detail: a change to a dependency means a new body
produced by the view.

Since a `View` body is also a `View` which is the definition of a piece of
user interact-able content, this process may trigger SwiftUI to update the
view representation in its implementation level in the coming processes.

However, is that true that each change to a dependency means a new body
produced by the view?

The answer is **no**. This is what I've learned from the experiments that
extend the original demo code in the WWDC session video with all the kinds
of dependencies that a developer could leverage.

The behaviors of the dependencies dealing with changes are instructive for
picking a proper kind of dependency when we have to take legacy code, app
architecture and performance at the same time. Let's study this by walking
through what I've done.

## Experiment Walk Through

First, this is the original demo code:

```swift
// TODO: Draw the dependency graph and put it by the side
struct DogView: View {

  @Binding var dog: Dog
  var treat: Treat

  var body: some View {
    Button {
      dog.reward(treat)
    } label: {
      PawView()
    }
  }

}
```

Since `@Binding` can only be a `Binding\.constant` which just means a
constant when it was not projected from upstreams like `@State`,
`@ObservedObject`, `@StateObject` and `@EnvironmentObject`, we must give
it a proper upstream to make the data flow.

Of course, `@Binding` is not the only dependency of a `View` in SwiftUI --
its upstreams, plain value, `@Environment` and `Observable` instances and
`@Bindable` that comes with Swift Observation could also be dependencies
of a `View`. We must also check these dependencies out.

On top of that, do not forget `UIView(Controller)Representable`, a
protocol derived from the `View` protocol. The view structs conform to
this protocol could also have dependencies. Additionally, during the
execution of `makeUIView(Controller)(context:)` and
`updateUIView(Controller)(context:)`, developers can access the
`EnvironmentValues` that come with the given `context` instance. This is
an additional dependency that can be made use of for conformers of
`UIView(Controller)Representable`.

By combining all the dependencies mentioned above, we can have the
following table to have a full glance at them.

| Dependencies                            | Available in                    | Code Examples                                                                |
|:----------------------------------------|:--------------------------------|:-----------------------------------------------------------------------------|
| Plain value                             | View                            | `var foo: Int`                                                               |
| State                                   | View                            | `@State var foo: Int`                                                        |
| ObservedObject                          | View                            | `@ObservedObject var foo: MyObservableObject`                                |
| StateObject                             | View                            | `@StateObject var foo: MyObservableObject`                                   |
| EnvironmentObject                       | View                            | `@EnvironmentObject var foo: MyObservableObject`                             |
| Binding with State upstream             | View                            | `@Binding var foo: Int` where `foo` is projected from a `State`              |
| Binding with ObservedObject upstream    | View                            | `@Binding var foo: Int` where `foo` is projected from an `ObservedObject`    |
| Binding with StateObject upstream       | View                            | `@Binding var foo: Int` where `foo` is projected from a `StateObject`        |
| Binding with EnvironmentObject upstream | View                            | `@Binding var foo: Int` where `foo` is projected from an `EnvironmentObject` |
| Environment                             | View                            | `@Environment(\.colorScheme) var colorScheme`                                |
| EnvironmentValues                       | UIView(Controller)Representable | `context.environment.colorScheme`                                            |
| Observable instance                     | View                            | `var foo: MySwiftObservationObject`                                          |
| Bindable                                | View                            | `@Bindable var foo: MySwiftObservationObject`                                |

> `UIView(Controller)Representable` inherits `View` protocol.

At the same time, I've already built a demo to showcase the differences in
new view body produce behavior for all these dependencies.

// TODO: Project code

## Observations

## Why SwiftUI Behaves Like This

## Suggestions
